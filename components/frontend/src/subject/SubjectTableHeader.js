import { Menu, Table } from "semantic-ui-react";
import { ColumnMenuItem, HamburgerMenu } from "../widgets/HamburgerMenu";
import { SortableTableHeaderCell } from '../widgets/SortableTableHeaderCell';
import { pluralize } from "../utils";

export function SubjectTableHeader(
    {
        clearVisibleDetailsTabs,
        columnDates,
        handleSort,
        hiddenColumns,
        hideMetricsNotRequiringAction,
        setHideMetricsNotRequiringAction,
        setDateInterval,
        setNrDates,
        sortColumn,
        sortDirection,
        toggleHiddenColumn,
        dateInterval,
        nrDates,
        visibleDetailsTabs
    }) {
    const sortProps = { sortColumn: sortColumn, sortDirection: sortDirection, handleSort: handleSort }
    return (
        <Table.Header>
            <Table.Row>
                <Table.HeaderCell className="unsortable" textAlign="center">
                    <HamburgerMenu>
                        <Menu.Item key="collapse_metrics" disabled={visibleDetailsTabs.length === 0} onClick={() => clearVisibleDetailsTabs()}>
                            Collapse all metrics
                        </Menu.Item>
                        <Menu.Item onClick={() => setHideMetricsNotRequiringAction(!hideMetricsNotRequiringAction)}>
                            {hideMetricsNotRequiringAction ? 'Show all metrics' : 'Hide metrics not requiring action'}
                        </Menu.Item>
                        <Menu.Item key="hide_columns">
                            <Menu.Header>Toggle visibility of columns</Menu.Header>
                            <Menu.Menu>
                                <ColumnMenuItem column="trend" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                                <ColumnMenuItem column="status" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                                <ColumnMenuItem column="measurement" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                                <ColumnMenuItem column="target" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                                <ColumnMenuItem column="source" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                                <ColumnMenuItem column="comment" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                                <ColumnMenuItem column="issues" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                                <ColumnMenuItem column="tags" hiddenColumns={hiddenColumns} toggleHiddenColumn={toggleHiddenColumn} />
                            </Menu.Menu>
                        </Menu.Item>
                        <Menu.Item key="nr_dates">
                            <Menu.Header>Number of dates</Menu.Header>
                            <Menu.Menu>
                                {[1, 2, 3, 4, 5, 6, 7].map((nr) =>
                                    <Menu.Item key={nr} active={nr === nrDates} onClick={() => setNrDates(nr)}>{`${nr} ${pluralize("date", nr)}`}</Menu.Item>
                                )}
                            </Menu.Menu>
                        </Menu.Item>
                        <Menu.Item key="time_between_dates">
                            <Menu.Header>Time between dates</Menu.Header>
                            <Menu.Menu>
                                <Menu.Item key={1} active={1 === dateInterval} onClick={() => setDateInterval(1)}>1 day</Menu.Item>
                                {[7, 14, 21, 28].map((nr) =>
                                    <Menu.Item key={nr} active={nr === dateInterval} onClick={() => setDateInterval(nr)}>{`${nr / 7} ${pluralize("week", nr / 7)}`}</Menu.Item>
                                )}
                            </Menu.Menu>
                        </Menu.Item>
                    </HamburgerMenu>
                </Table.HeaderCell>
                <SortableTableHeaderCell column='name' label='Metric' {...sortProps} />
                {nrDates > 1 && columnDates.map(date => <Table.HeaderCell key={date} className="unsortable" textAlign="right">{date.toLocaleDateString()}</Table.HeaderCell>)}
                {nrDates > 1 && <SortableTableHeaderCell column="unit" label="Unit" {...sortProps} />}
                {nrDates === 1 && !hiddenColumns.includes("trend") && <Table.HeaderCell className="unsortable" width="2">Trend (7 days)</Table.HeaderCell>}
                {nrDates === 1 && !hiddenColumns.includes("status") && <SortableTableHeaderCell column='status' label='Status' textAlign='center' {...sortProps} />}
                {nrDates === 1 && !hiddenColumns.includes("measurement") && <SortableTableHeaderCell column='measurement' label='Measurement' {...sortProps} />}
                {nrDates === 1 && !hiddenColumns.includes("target") && <SortableTableHeaderCell column='target' label='Target' {...sortProps} />}
                {!hiddenColumns.includes("source") && <SortableTableHeaderCell column='source' label='Source' {...sortProps} />}
                {!hiddenColumns.includes("comment") && <SortableTableHeaderCell column='comment' label='Comment' {...sortProps} />}
                {!hiddenColumns.includes("issues") && <SortableTableHeaderCell column='issues' label='Issues' {...sortProps} />}
                {!hiddenColumns.includes("tags") && <SortableTableHeaderCell column='tags' label='Tags' {...sortProps} />}
            </Table.Row>
        </Table.Header>
    )
}