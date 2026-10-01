import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, List, Tuple
from utils.logger import get_logger

logger = get_logger("cv_service")

class CVAnalysisService:
    def __init__(self):
        # Carregamento do Classificador Haar Cascade para detecção de rostos
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def analyze_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Executa pipeline completo de análise de visão computacional na imagem informada.
        """
        try:
            # Conversão de bytes para formato OpenCV (BGR)
            file_bytes = np.frombuffer(image_bytes, dtype=np.uint8)
            img_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            if img_bgr is None:
                raise ValueError("Incapaz de decodificar a imagem informada.")

            height, width, _ = img_bgr.shape
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

            # 1. Detecção de Rostos e Pessoas
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            num_faces = len(faces)
            num_people = num_faces  # Estimatativa baseada em detecção facial

            # 2. Métricas da Imagem (Luminosidade e Nitidez)
            mean_luminance = float(np.mean(gray))
            luminosity_str = self._assess_luminosity(mean_luminance)

            laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
            sharpness_str = self._assess_sharpness(laplacian_var)

            # 3. Análise de Cores Dominantes
            dominant_colors = self._extract_dominant_colors(img_bgr, k=3)

            # 4. Detecção genérica de contornos/objetos
            detected_objects = self._detect_contours_and_shapes(gray, num_faces)

            # 5. Descrição gerada automaticamente
            description = (
                f"Imagem de resolução {width}x{height}px com iluminação {luminosity_str.lower()} "
                f"e qualidade de nitidez {sharpness_str.lower()}. "
                f"Foram identificados {num_faces} rosto(s) em cena."
            )

            result = {
                "resolucao": f"{width}x{height}",
                "descricao": description,
                "objetos": detected_objects,
                "quantidade_pessoas": num_people,
                "rostos": num_faces,
                "idade": "Indeterminado (Sem IA Externa)",
                "emocao": "Neutro (Sem IA Externa)",
                "luminosidade": f"{luminosity_str} ({mean_luminance:.1f})",
                "nitidez": f"{sharpness_str} (Var: {laplacian_var:.1f})",
                "cores": dominant_colors,
                "raw_metrics": {
                    "width": width,
                    "height": height,
                    "luminance_mean": mean_luminance,
                    "laplacian_var": laplacian_var
                }
            }
            logger.info("Análise de Visão Computacional concluída com sucesso.")
            return result

        except Exception as e:
            logger.error(f"Erro durante o processamento de imagem OpenCV: {str(e)}")
            raise e

    def _assess_luminosity(self, mean_lum: float) -> str:
        if mean_lum < 70:
            return "Baixa (Escura)"
        elif mean_lum > 180:
            return "Alta (Muito Clara)"
        return "Adequada (Equilibrada)"

    def _assess_sharpness(self, laplacian_var: float) -> str:
        if laplacian_var < 100:
            return "Baixa (Desfocada)"
        elif laplacian_var < 500:
            return "Média (Aceitável)"
        return "Alta (Nítida)"

    def _extract_dominant_colors(self, img_bgr: np.ndarray, k: int = 3) -> List[str]:
        pixels = img_bgr.reshape(-1, 3).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        centers = centers.astype(int)
        hex_colors = []
        for b, g, r in centers:
            hex_colors.append(f"#{r:02x}{g:02x}{b:02x}")
        return hex_colors

    def _detect_contours_and_shapes(self, gray_img: np.ndarray, faces_count: int) -> List[str]:
        objects = []
        if faces_count > 0:
            objects.append(f"{faces_count} Pessoa(s)/Rosto(s)")

        blurred = cv2.GaussianBlur(gray_img, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        structural_objects = 0
        for c in contours:
            if cv2.contourArea(c) > 1000:
                structural_objects += 1

        if structural_objects > 0:
            objects.append(f"{structural_objects} Formas/Objetos Estruturados")

        if not objects:
            objects.append("Nenhum objeto proeminente detectado")

        return objects
