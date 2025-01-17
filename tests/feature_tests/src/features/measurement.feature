Feature: measurement
  Measuring metrics

  Background: a report with a subject and a metric exists
    Given a logged-in client
    And an existing report
    And an existing subject
    And an existing metric

  Scenario: the metric has no source
    When the collector gets the metrics to measure
    Then the metric needs to be measured

  Scenario: the metric has no source but an issue
    When the client changes the metric issue_ids to "123"
    And the client changes the report tracker_type to "jira"
    And the client changes the report tracker_url to "https://jira"
    When the collector gets the metrics to measure
    Then the metric needs to be measured

  Scenario: the metric is measured and meets the target
    Given an existing source
    When the collector measures "0"
    Then the metric status is "target_met"

  Scenario: the metric is measured and doesn't meet the target
    Given an existing source
    When the collector measures "100"
    Then the metric status is "target_not_met"

  Scenario: the metric has a percentage scale
    Given an existing metric with type "performancetest_stability"
    And an existing source with type "performancetest_runner"
    When the collector measures "50"
    Then the metric status is "target_not_met"

  Scenario: the metric has a percentage scale with sum as addition method
    Given an existing metric with type "complex_units"
    And an existing source with type "sonarqube"
    When the collector measures "420"
    Then the metric status is "target_not_met"

  Scenario: the metric has a percentage scale and measures total 0
    Given an existing metric with type "performancetest_stability"
    And an existing source with type "performancetest_runner"
    When the collector measures "0" with total "0"
    Then the metric status is "target_met"

  Scenario: the metric has a version number scale
    Given an existing metric with type "source_version"
    And an existing source with type "owasp_dependency_check"
    When the client changes the metric target to "1.2.2"
    And the collector measures "1.2.3"
    Then the metric status is "target_met"

  Scenario: the metric has a version number scale, but the measurement target is invalid
    Given an existing metric with type "source_version"
    And an existing source with type "owasp_dependency_check"
    When the collector measures "2.3.4"
    And the client changes the metric target to "invalid version"
    Then the metric status is "target_met"

  Scenario: the metric is measured but an error happens
    Given an existing source
    When the collector encounters a parse error
    Then the metric status is "None"
    When the client waits a second
    When the collector measures "0"
    Then the metric status is "target_met"

  Scenario: the metric has a version number scale, and an error happens while measuring
    Given an existing metric with type "source_version"
    And an existing source with type "owasp_dependency_check"
    When the collector encounters a parse error
    Then the metric status is "None"
    When the client waits a second
    When the collector measures "1.2.3"
    Then the metric status is "target_met"

  Scenario: the metric is measured but deleted while being measured
    Given an existing source
    When the client deletes the metric
    And the collector measures "100"
    Then the metric has no measurements

  Scenario: the metric has no source and therefor is not measured yet and this is accepted as technical debt
    When the client changes the metric accept_debt to "True"
    Then the metric status is "debt_target_met"

  Scenario: the metric has a source but is not measured yet and this is accepted as technical debt
    Given an existing source
    When the client changes the metric accept_debt to "True"
    Then the metric status is "debt_target_met"

  Scenario: the metric has a source that is measured, but without value, and this is accepted as technical debt
    Given an existing source
    When the collector encounters a parse error
    Then the metric status is "None"
    When the client changes the metric accept_debt to "True"
    Then the metric status is "debt_target_met"

  Scenario: the metric has a source that is measured, but then the source is removed, and this is accepted as technical debt
    Given an existing source
    When the collector encounters a parse error
    Then the metric status is "None"
    When the client deletes the source
    And the client changes the metric accept_debt to "True"
    Then the metric status is "debt_target_met"

  Scenario: the metric is measured, doesn't meet the target, and it's accepted as technical debt
    Given an existing source
    When the collector measures "100"
    When the client waits a second
    And the client changes the metric accept_debt to "True"
    When the client waits a second
    And the client changes the metric debt_target to "100"
    Then the metric status is "debt_target_met"

  Scenario: the metric is measured and has expired accepted technical debt
    Given an existing source
    When the collector measures "100"
    When the client waits a second
    And the client changes the metric accept_debt to "True"
    When the client waits a second
    And the client changes the metric debt_target to "100"
    Then the metric status is "debt_target_met"
    When the client changes the metric debt_end_date to "2020-01-01"
    When the client waits a second
    And the collector measures "100"
    Then the metric status is "target_not_met"

  Scenario: the metric has accepted technical debt is changed to informative
    Given an existing source
    When the collector measures "100"
    And the client waits a second
    And the client changes the metric accept_debt to "True"
    And the client waits a second
    And the client changes the metric debt_target to "100"
    And the client waits a second
    Then the metric status is "debt_target_met"
    When the client changes the metric evaluate_targets to "False"
    And the client waits a second
    Then the metric status is "informative"

  Scenario: a measurement that's unchanged is updated
    Given an existing source
    When the collector measures "0"
    And the collector measures "0"
    Then the metric has one measurement

  Scenario: a new metric has no old measurements
    Given an existing source
    When the collector measures "0"
    Then the metric had no measurements

  Scenario: get the reports overview measurements
    When the client gets the current reports overview measurements
    Then the server returns the reports overview measurements

  Scenario: get the reports overview measurements with time travel
    When the client creates a report
    And the client creates a subject
    And the client creates a metric
    And the client waits a second
    And the client gets past reports overview measurements
    Then the server returns the reports overview measurements