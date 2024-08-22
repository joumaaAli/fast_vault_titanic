from sdv.evaluation.single_table import evaluate_quality

def evaluate_synthetic_data(synthetic_data, real_data, metadata):
    return evaluate_quality(real_data, synthetic_data, metadata)