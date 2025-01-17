import { useEffect, useState } from 'react';
import { PERMISSIONS } from './context/Permissions';
import { HyperLink } from './widgets/HyperLink';
import { metricReactionDeadline } from './defaults';

export const MILLISECONDS_PER_HOUR = 60 * 60 * 1000;
const MILLISECONDS_PER_DAY = 24 * MILLISECONDS_PER_HOUR;

export const STATUSES = ["unknown", "target_not_met", "near_target_met", "target_met", "debt_target_met", "informative"];
export const STATUS_COLORS = {
    informative: "blue",
    target_met: "green",
    near_target_met: "yellow",
    target_not_met: "red",
    debt_target_met: "grey",
    unknown: "white"
}
export const STATUS_COLORS_RGB = {
    target_not_met: "rgb(211,59,55)",
    target_met: "rgb(30,148,78)",
    near_target_met: "rgb(253,197,54)",
    debt_target_met: "rgb(150,150,150)",
    informative: "rgb(0,165,255)",
    unknown: "rgb(245,245,245)"
}
export const STATUS_NAME = {
    informative: "Informative",
    target_met: "Target met",
    near_target_met: "Near target met",
    target_not_met: "Target not met",
    debt_target_met: "Technical debt target met",
    unknown: "Unknown"
}
export const STATUS_DESCRIPTION = {
    "informative": `${STATUS_NAME.informative}: the measurement value is not evaluated against a target value.`,
    "target_met": `${STATUS_NAME.target_met}: the measurement value meets the target value.`,
    "near_target_met": `${STATUS_NAME.near_target_met}: the measurement value is close to the target value.`,
    "target_not_met": `${STATUS_NAME.target_not_met}: the measurement value does not meet the target value.`,
    "debt_target_met": <>{`${STATUS_NAME.debt_target_met}: the measurement value does not meet the\ntarget value, but this is accepted as `}<HyperLink url="https://en.wikipedia.org/wiki/Technical_debt">technical debt</HyperLink>{". The measurement\nvalue does meet the technical debt target."}</>,
    "unknown": `${STATUS_NAME.unknown}: the status could not be determined because no sources have\nbeen configured for the metric yet or the measurement data could not\nbe collected.`
}

export function getMetricDirection(metric, dataModel) {
    // Old versions of the datamodel may contain the unicode version of the direction, be prepared:
    return { "≦": "<", "≧": ">", "<": "<", ">": ">" }[metric.direction || dataModel.metrics[metric.type].direction];
}

export function formatMetricDirection(metric, dataModel) {
    return { "<": "≦", ">": "≧" }[getMetricDirection(metric, dataModel)];
}

export function get_metric_name(metric, datamodel) {
    return metric.name || datamodel.metrics[metric.type].name;
}

export function get_source_name(source, datamodel) {
    return source.name || datamodel.sources[source.type].name;
}

export function get_subject_name(subject, datamodel) {
    return subject.name || datamodel.subjects[subject.type].name;
}

export function get_metric_target(metric) {
    return metric.target || "0";
}

export function getMetricUnit(metric, dataModel) {
    const metricType = dataModel.metrics[metric.type];
    return formatMetricUnit(metricType, metric)
}

export function getMetricResponseDeadline(metric, report) {
    let deadline = null;
    if (metric.status === "debt_target_met") {
        if (metric.debt_end_date) {
            deadline = new Date(metric.debt_end_date)
        }
    } else if ((metric.status || "unknown") in metricReactionDeadline && metric.status_start) {
        deadline = new Date(metric.status_start)
        deadline.setDate(deadline.getDate() + getMetricDesiredResponseTime(report, metric.status))
    }
    return deadline
}

export function getMetricResponseTimeLeft(metric, report) {
    const deadline = getMetricResponseDeadline(metric, report)
    const now = new Date()
    return deadline === null ? null : deadline.getTime() - now.getTime()
}

function getMetricResponseOverruns(metric_uuid, metric, measurements) {
    const scale = metric?.scale ?? "count"
    let previousStatus;
    const consolidatedMeasurements = [];
    const filteredMeasurements = measurements.filter((measurement) => measurement.metric_uuid === metric_uuid)
    filteredMeasurements.forEach((measurement) => {
        const status = measurement?.[scale]?.status || "unknown"
        if (status === previousStatus) {
            consolidatedMeasurements.at(-1).end = measurement.end  // Status unchanged so merge this measurement with the previous one
        } else {
            consolidatedMeasurements.push(measurement);  // Status changed or first one, so keep this measurement
        }
        previousStatus = status
    })
    return consolidatedMeasurements
}

export function getMetricResponseOverrun(metric_uuid, metric, report, measurements) {
    const consolidatedMeasurements = getMetricResponseOverruns(metric_uuid, metric, measurements)
    const scale = metric?.scale ?? "count"
    let totalOverrun = 0;  // Amount of time the desired response time was not achieved for this metric
    const overruns = []
    consolidatedMeasurements.forEach((measurement) => {
        const status = measurement?.[scale]?.status || "unknown"
        if (status in metricReactionDeadline) {
            const desiredResponseTime = getMetricDesiredResponseTime(report, status) * MILLISECONDS_PER_DAY;
            const actualResponseTime = (new Date(measurement.end)).getTime() - (new Date(measurement.start)).getTime()
            const overrun = Math.max(0, actualResponseTime - desiredResponseTime)
            if (overrun > 0) {
                overruns.push(
                    {
                        status: status,
                        start: measurement.start,
                        end: measurement.end,
                        desired_response_time: days(desiredResponseTime),
                        actual_response_time: days(actualResponseTime),
                        overrun: days(overrun)
                    }
                )
                totalOverrun += overrun
            }
        }
    })
    return { totalOverrun: days(totalOverrun), overruns: overruns }
}

function getMetricDesiredResponseTime(report, status) {
    return report?.desired_response_times?.[status] ?? (metricReactionDeadline[status] ?? metricReactionDeadline["unknown"])
}

export function get_metric_value(metric) {
    return metric?.latest_measurement?.[metric.scale]?.value ?? '';
}

export function get_metric_comment(metric) {
    return metric.comment ?? '';
}

export function getMetricScale(metric, dataModel) {
    return metric.scale || dataModel.metrics[metric.type].default_scale || "count"
}

export function get_metric_status(metric) {
    return metric.status ?? '';
}

export function getStatusName(status) {
    return {
        target_met: 'Target met', near_target_met: 'Near target met', debt_target_met: 'Debt target met',
        target_not_met: 'Target not met', informative: 'Informative', unknown: 'Unknown'
    }[status || "unknown"];
}

export function getMetricTags(metric) {
    const tags = metric.tags ?? [];
    tags.sort();
    return tags
}

export function getReportTags(report) {
    const tags = new Set();
    Object.values(report.subjects).forEach((subject) => {
        Object.values(subject.metrics).forEach((metric) => {
            getMetricTags(metric).forEach((tag) => tags.add(tag))
        })
    })
    const sortedTags = Array.from(tags);
    sortedTags.sort();
    return sortedTags
}

export function getReportsTags(reports) {
    const tags = new Set();
    reports.forEach((report) => {
        getReportTags(report).forEach((tag) => tags.add(tag))
    });
    const sortedTags = Array.from(tags);
    sortedTags.sort();
    return sortedTags
}

export function nrMetricsInReport(report) {
    let nrMetrics = 0;
    Object.values(report.subjects).forEach((subject) => {
        nrMetrics += Object.keys(subject.metrics).length ?? 0;
    });
    return nrMetrics
}

export function nrMetricsInReports(reports) {
    let nrMetrics = 0;
    reports.forEach((report) => {
        nrMetrics += nrMetricsInReport(report)
    })
    return nrMetrics
}

export function get_metric_issue_ids(metric) {
    let issue_ids = metric.issue_ids ?? [];
    issue_ids.sort();
    return issue_ids
}

export function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

export function pluralize(word, count) {
    // Pluralize (naively; it doesn't work for words like sheep) the word if count > 1
    return word + (count === 1 ? "" : "s");
}

export function nice_number(number) {
    let rounded_numbers = [10, 20, 30, 40, 50, 60, 70, 80, 90];
    do {
        for (let rounded_number of rounded_numbers) {
            if (number <= ((9 * rounded_number) / 10)) {
                return rounded_number
            }
        }
        rounded_numbers = rounded_numbers.map((value) => { return value * 10 });
    }
    while (true);
}

export function scaled_number(number) {
    const scale = ['', 'k', 'm'];
    const exponent = Math.floor(Math.log(number) / Math.log(1000));
    return (number / Math.pow(1000, exponent)).toFixed(0) + scale[exponent];
}

function formatMetricUnit(metricType, metric) {
    return `${metric.unit || metricType.unit}`;
}

export function formatMetricScale(metric) {
    return metric.scale === "percentage" ? "%" : "";
}

export function formatMetricScaleAndUnit(metricType, metric) {
    const scale = formatMetricScale(metric);
    const unit = formatMetricUnit(metricType, metric);
    const sep = unit ? " " : "";
    return `${scale}${sep}${unit}`;
}

export function days(timeInMs) {
    return Math.round(timeInMs / MILLISECONDS_PER_DAY)
}

const registeredURLSearchQueryKeys = new Set(["report_date", "report_url"]);

export function useURLSearchQuery(history, key, state_type, default_value) {
    // state_type can either be "boolean", "integer", "string", or "array"
    const [state, setState] = useState(getState());
    registeredURLSearchQueryKeys.add(key);

    function getState() {
        const parsed_state = parseURLSearchQuery().get(key);
        if (state_type === "boolean") {
            return parsed_state === "true"
        } else if (state_type === "integer") {
            return typeof parsed_state === "string" ? parseInt(parsed_state, 10) : default_value;
        } else if (state_type === "string") {
            return parsed_state ?? default_value
        }
        // else state_type is "array"
        return parsed_state?.split(",") ?? []
    }

    function parseURLSearchQuery() {
        return new URLSearchParams(history.location.search)
    }

    function setURLSearchQuery(new_state) {
        let parsed = parseURLSearchQuery();
        if ((state_type === "array" && new_state.length === 0) || (new_state === default_value)) {
            parsed.delete(key)
        } else {
            parsed.set(key, new_state)
        }
        const search = parsed.toString().replace(/%2C/g, ",")  // No need to encode commas
        history.replace({ search: search.length > 0 ? "?" + search : "" });
        setState(new_state);
    }

    function toggleURLSearchQuery(...items) {
        const new_state = [];
        state.forEach((item) => { if (!items.includes(item)) { new_state.push(item) } })
        items.forEach((item) => { if (!state.includes(item)) { new_state.push(item) } })
        setURLSearchQuery(new_state);
    }

    function clearURLSearchQuery() {
        setURLSearchQuery([]);
    }

    return state_type === "array" ? [state, toggleURLSearchQuery, clearURLSearchQuery] : [state, setURLSearchQuery]
}

export function registeredURLSearchParams(history) {
    // Return registered URL search parameters only; to prevent CodeQL js/client-side-unvalidated-url-redirection
    let parsed = new URLSearchParams(history.location.search)
    for (let key of parsed.keys()) {
        if (!registeredURLSearchQueryKeys.has(key)) { parsed.delete(key) }
    }
    return parsed
}

export function useDelayedRender() {
    const [visible, setVisible] = useState(false);
    useEffect(() => {
        const timeout = setTimeout(setVisible, 50, true);
        return () => clearTimeout(timeout)
    }, []);
    return visible;
}

export function isValidDate_YYYYMMDD(string) {
    if (/^\d{4}-\d{2}-\d{2}$/.test(string)) {
        const milliseconds_since_epoch = Date.parse(string);
        return !isNaN(milliseconds_since_epoch)
    }
    return false
}

export function getUserPermissions(username, email, current_report_is_tag_report, report_date, permissions) {
    if (username === null || report_date !== null || current_report_is_tag_report) { return [] }
    return PERMISSIONS.filter((permission) => {
        const permittedUsers = permissions?.[permission] ?? [];
        return permittedUsers.length === 0 ? true : permittedUsers.includes(username) || permittedUsers.includes(email)
    });
}

export function userPrefersDarkMode(uiMode) {
    return uiMode === "dark" || (uiMode === null && window.matchMedia?.('(prefers-color-scheme: dark)').matches)
}

export function dropdownOptions(options) {
    return options.map(option => ({ key: option, text: option, value: option }))
}

export function slugify(name) {
    return `#${name?.toLowerCase().replaceAll(" ", "-").replaceAll("(", "").replaceAll(")", "")}`
}

export function sum(object) {
    const list = typeof object == Array ? object : Object.values(object)
    return list.reduce((a, b) => a + b, 0)
}
