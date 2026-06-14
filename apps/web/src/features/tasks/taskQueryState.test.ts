import { describe, expect, it } from 'vitest';
import { hasActiveFilters, searchToParams, validateTaskSearch } from './taskQueryState';

describe('validateTaskSearch', () => {
  it('keeps valid enum arrays and values, dropping unknowns', () => {
    const result = validateTaskSearch({
      status: ['todo', 'bogus'],
      priority: ['high'],
      assignee: ['u1', 2],
      label: ['l1'],
      due: 'overdue',
      sort: 'priority',
      cancelled: true,
    });
    expect(result).toEqual({
      status: ['todo'],
      priority: ['high'],
      assignee: ['u1'],
      label: ['l1'],
      due: 'overdue',
      sort: 'priority',
      cancelled: true,
    });
  });

  it('coerces empties and invalid scalars to undefined', () => {
    expect(validateTaskSearch({ status: [], due: 'someday', sort: 1, cancelled: 'yes' })).toEqual({
      status: undefined,
      assignee: undefined,
      priority: undefined,
      label: undefined,
      due: undefined,
      sort: undefined,
      cancelled: undefined,
    });
  });
});

describe('searchToParams', () => {
  it('passes filters through and includes cancelled when requested', () => {
    expect(searchToParams({ status: ['todo'], cancelled: true, sort: 'due_date' })).toEqual({
      status: ['todo'],
      assignee: undefined,
      priority: undefined,
      label: undefined,
      due: undefined,
      sort: 'due_date',
      include_cancelled: true,
    });
  });

  it('includes cancelled when the status filter selects it explicitly', () => {
    expect(searchToParams({ status: ['cancelled'] }).include_cancelled).toBe(true);
  });

  it('leaves include_cancelled undefined by default', () => {
    expect(searchToParams({}).include_cancelled).toBeUndefined();
  });
});

describe('hasActiveFilters', () => {
  it('is false for an empty or sort-only search', () => {
    expect(hasActiveFilters({})).toBe(false);
    expect(hasActiveFilters({ sort: 'priority' })).toBe(false);
  });

  it('is true when any filter dimension is set', () => {
    expect(hasActiveFilters({ status: ['todo'] })).toBe(true);
    expect(hasActiveFilters({ assignee: ['u1'] })).toBe(true);
    expect(hasActiveFilters({ priority: ['high'] })).toBe(true);
    expect(hasActiveFilters({ label: ['l1'] })).toBe(true);
    expect(hasActiveFilters({ due: 'today' })).toBe(true);
    expect(hasActiveFilters({ cancelled: true })).toBe(true);
  });
});
