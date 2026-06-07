import { useIntl } from 'react-intl';
import { Button, ConfirmDialog, LabelChip } from '@/components/ui';
import { Pencil } from '@/components/ui/icons';
import { LabelModal } from './LabelModal';
import { useDeleteLabel, useLabels } from './useLabels';

/**
 * Labels settings tab (DRD §8.9): the workspace label set with create/edit
 * modals and a delete confirmation. Empty state nudges the first label.
 */
export function LabelsTab() {
  const intl = useIntl();
  const { data } = useLabels();
  const deleteLabel = useDeleteLabel();
  const labels = data?.labels ?? [];

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-[15px] font-semibold text-text-primary">
          {intl.formatMessage({ id: 'settings.labels.heading' })}
        </h2>
        <LabelModal
          trigger={
            <Button size="sm">{intl.formatMessage({ id: 'settings.labels.create' })}</Button>
          }
        />
      </div>

      {labels.length === 0 ? (
        <p className="text-[13px] text-text-tertiary">
          {intl.formatMessage({ id: 'settings.labels.empty' })}
        </p>
      ) : (
        <ul className="flex flex-col">
          {labels.map((label) => (
            <li
              key={label.id}
              className="flex items-center gap-3 border-b border-divider py-2.5 last:border-b-0"
            >
              <span className="flex-1">
                <LabelChip name={label.name} color={label.color} />
              </span>
              <LabelModal
                label={label}
                trigger={
                  <button
                    type="button"
                    className="rounded-sm p-1.5 text-text-tertiary hover:bg-bg-hover hover:text-text-primary"
                    aria-label={intl.formatMessage({ id: 'settings.labels.edit' })}
                  >
                    <Pencil size={16} strokeWidth={1.75} />
                  </button>
                }
              />
              <ConfirmDialog
                trigger={
                  <Button type="button" variant="ghost" size="sm">
                    {intl.formatMessage({ id: 'settings.labels.delete' })}
                  </Button>
                }
                title={intl.formatMessage({ id: 'settings.labels.deleteTitle' })}
                description={intl.formatMessage(
                  { id: 'settings.labels.deleteBody' },
                  { name: label.name },
                )}
                confirmLabel={intl.formatMessage({ id: 'settings.labels.deleteConfirm' })}
                onConfirm={() => deleteLabel.mutateAsync(label.id)}
                pending={deleteLabel.isPending}
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
