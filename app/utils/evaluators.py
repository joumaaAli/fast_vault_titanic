from sdmetrics.reports.single_table import QualityReport

def evaluate_data_quality(synthetic_data, real_data, metadata):
    quality_report = QualityReport()
    quality_report.generate(real_data, synthetic_data, metadata.to_dict())

    # Extract the relevant scores
    column_shapes_score = quality_report.get_details("Column Shapes")["Score"].mean()
    column_pair_trends_score = quality_report.get_details("Column Pair Trends")["Score"].mean()
    overall_score = quality_report.get_score()

    return {
        "Column Shapes Score": column_shapes_score,
        "Column Pair Trends Score": column_pair_trends_score,
        "Overall Score": overall_score
    }
