from sdv.single_table import CTGANSynthesizer, GaussianCopulaSynthesizer, CopulaGANSynthesizer


class SynthesizerFactory:
    @staticmethod
    def get_synthesizer(synthesizer_type, metadata):
        if synthesizer_type == "ctgan":
            return CTGANSynthesizer(metadata)
        elif synthesizer_type == "copulagan":
            return CopulaGANSynthesizer(metadata)
        elif synthesizer_type == "gaussiancopula":
            return GaussianCopulaSynthesizer(metadata)
        else:
            raise ValueError(f"Unsupported synthesizer type: {synthesizer_type}")