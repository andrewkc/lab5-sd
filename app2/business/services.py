import json
import subprocess
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from data.database import db
from data.models import Campaign
from data.repositories import CampaignRepository


class ScriptGenerator:
    def generate(self, filename):
        product = Path(filename).stem.replace("_", " ").replace("-", " ").title()
        return [
            {"title": "Impacto en 15 segundos", "hook": f"Descubre {product}.", "body": "Una solución pensada para destacar tu marca desde el primer vistazo.", "cta": "Conócela hoy."},
            {"title": "Historia de marca", "hook": "Tu marca merece ser recordada.", "body": "Presenta lo que haces, conecta con tu audiencia y convierte atención en acción.", "cta": "Comparte tu historia."},
            {"title": "Oferta irresistible", "hook": "Esto es lo que estabas buscando.", "body": "Muestra el valor de tu producto con una propuesta clara, visual y fácil de compartir.", "cta": "Escríbenos ahora."},
        ]


class CreativeGenerator:
    def __init__(self, storage_dir):
        self.storage_dir = Path(storage_dir)

    def _font(self, size):
        for name in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "arial.ttf"):
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()

    def _wrapped_text(self, draw, text, font, max_width):
        words, lines, current = text.split(), [], ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def generate(self, source_path, scripts, output_dir):
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        original = Image.open(source_path).convert("RGB")
        colors = [(13, 35, 72), (102, 37, 91), (12, 93, 92)]
        paths = []
        for index, (script, color) in enumerate(zip(scripts, colors), start=1):
            canvas = ImageOps.fit(original, (1080, 1080), method=Image.Resampling.LANCZOS)
            overlay = Image.new("RGBA", canvas.size, color + (105,))
            canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay)
            draw = ImageDraw.Draw(canvas)
            title_font, body_font, cta_font = self._font(58), self._font(34), self._font(42)
            draw.rounded_rectangle((54, 54, 1026, 1026), radius=28, outline=(255, 255, 255, 210), width=4)
            draw.text((95, 105), f"CAMPAÑA {index}", fill=(255, 220, 120), font=self._font(28))
            y = 650
            for line in self._wrapped_text(draw, script["hook"], title_font, 850):
                draw.text((95, y), line, fill="white", font=title_font)
                y += 70
            for line in self._wrapped_text(draw, script["body"], body_font, 850):
                draw.text((95, y + 25), line, fill=(240, 244, 250), font=body_font)
                y += 45
            draw.text((95, 930), script["cta"], fill=(255, 220, 120), font=cta_font)
            path = output / f"creative-{index}.png"
            canvas.convert("RGB").save(path, quality=92)
            paths.append(path)
        video_path = output / "campaign-video.mp4"
        command = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", "1/2", "-start_number", "1", "-i", str(output / "creative-%d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-vf", "format=yuv420p", str(video_path)]
        try:
            subprocess.run(command, check=True, capture_output=True)
        except (FileNotFoundError, subprocess.CalledProcessError) as error:
            raise RuntimeError("No se pudo generar el video. Verifica que FFmpeg esté instalado.") from error
        return paths, video_path


class MarketingService:
    def __init__(self, storage_dir, repository=None):
        self.storage_dir = Path(storage_dir)
        self.repository = repository or CampaignRepository()
        self.script_generator = ScriptGenerator()
        self.creative_generator = CreativeGenerator(storage_dir)

    def create_campaign(self, uploaded_file):
        if not uploaded_file or not uploaded_file.filename:
            raise ValueError("Selecciona una imagen")
        allowed = {".jpg", ".jpeg", ".png", ".webp"}
        suffix = Path(uploaded_file.filename).suffix.lower()
        if suffix not in allowed:
            raise ValueError("Formato no soportado. Usa JPG, PNG o WEBP")
        campaign_id = uuid.uuid4().hex
        upload_dir = self.storage_dir / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        relative_path = Path("uploads") / f"{campaign_id}{suffix}"
        absolute_path = self.storage_dir / relative_path
        uploaded_file.save(absolute_path)
        scripts = self.script_generator.generate(uploaded_file.filename)
        campaign = Campaign(original_filename=uploaded_file.filename, image_path=str(relative_path), scripts_json=json.dumps(scripts, ensure_ascii=False))
        return self.repository.create(campaign)

    def scripts(self, campaign):
        return json.loads(campaign.scripts_json)

    def generate_assets(self, campaign, script_index, platform):
        try:
            script_index = int(script_index)
        except (TypeError, ValueError) as error:
            raise ValueError("Selecciona un guion válido") from error
        scripts = self.scripts(campaign)
        if script_index not in range(3):
            raise ValueError("Selecciona uno de los tres guiones")
        source = self.storage_dir / campaign.image_path
        output_dir = self.storage_dir / "campaigns" / str(campaign.id)
        selected_script = scripts[script_index]
        image_paths, video_path = self.creative_generator.generate(source, [selected_script, selected_script, selected_script], output_dir)
        campaign.selected_script = script_index
        campaign.social_platform = platform
        campaign.social_status = "ready_to_publish"
        for asset in list(campaign.assets):
            db.session.delete(asset)
        db.session.commit()
        for path in image_paths:
            self.repository.add_asset(campaign.id, "image", str(path.relative_to(self.storage_dir)))
        self.repository.add_asset(campaign.id, "video", str(video_path.relative_to(self.storage_dir)))
        return campaign

    def publish(self, campaign):
        if campaign.selected_script is None:
            raise ValueError("Primero selecciona un guion y genera los contenidos")
        if campaign.social_platform not in {"instagram", "tiktok"}:
            raise ValueError("Selecciona Instagram o TikTok")
        campaign.social_status = "published_simulated"
        self.repository.update(campaign)
        return campaign
