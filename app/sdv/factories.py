from sdv.single_table import CTGANSynthesizer, GaussianCopulaSynthesizer
from sdv.multi_table import HMASynthesizer
from sdv.sequential import PARSynthesizer
from sdv.metadata import SingleTableMetadata, MultiTableMetadata

class SynthesizerFactory:
    @staticmethod
    def get_synthesizer(synthesizer_type: str, metadata):
        if synthesizer_type == "ctgan":
            return CTGANSynthesizer(metadata)
        elif synthesizer_type == "gaussian_copula":
            return GaussianCopulaSynthesizer(metadata)
        elif synthesizer_type == "hma":
            return HMASynthesizer(metadata)
        elif synthesizer_type == "par":
            return PARSynthesizer(metadata)
        else:
            raise ValueError("Unsupported synthesizer type")
