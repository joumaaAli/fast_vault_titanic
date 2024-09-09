from sdv.single_table import CTGANSynthesizer, GaussianCopulaSynthesizer, CopulaGANSynthesizer
from app.entities.synthetic_data import SynthesizerType  # Import the enum

class SynthesizerFactory:
    @staticmethod
    def get_synthesizer(synthesizer_type: SynthesizerType, metadata):
        if synthesizer_type == SynthesizerType.ctgan:
            return CTGANSynthesizer(metadata)
        elif synthesizer_type == SynthesizerType.copulagan:
            return CopulaGANSynthesizer(metadata)
        elif synthesizer_type == SynthesizerType.gaussiancopula:
            return GaussianCopulaSynthesizer(metadata)
        else:
            raise ValueError(f"Unsupported synthesizer type: {synthesizer_type}")
