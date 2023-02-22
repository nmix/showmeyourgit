def test_one_file_values(one_file_modifications_converted):
    edge = one_file_modifications_converted[0]
    assert edge.added == 8
    assert edge.deleted == 4
    assert edge.churn == 4
    assert edge.ratio == 50.0
    assert edge.churn_ratio == 50.0


def test_multiple_files_values(multiple_files_modifications_converted):
    file1, file2, file3 = multiple_files_modifications_converted
    # ---
    assert file1.added == 3
    assert file1.deleted == 1
    assert file1.churn == 0
    # ---
    assert file2.added == 1
    assert file2.deleted == 1
    assert file2.churn == 1
    # ---
    assert file3.added == 4
    assert file3.deleted == 2
    assert file3.churn == 2
