import { useIntl } from 'react-intl';
import type { Invitation, Member } from '@/api/types';
import { Avatar, Button, ConfirmDialog, Select } from '@/components/ui';
import { useCurrentUser } from '@/hooks/useCurrentUser';
import { cn } from '@/lib/cn';
import { formatRelativeTime } from '@/lib/relativeTime';
import { InviteMemberModal } from './InviteMemberModal';
import { useInvitations, useResendInvitation } from './useInvitations';
import { useChangeRole, useMembers, useRemoveMember } from './useMembers';

/**
 * Members settings tab (DRD §8.8): member table (role dropdown + Owner-only
 * remove) and the invitation table (status badge + resend), plus the Invite
 * Member modal.
 */
export function MembersTab() {
  const intl = useIntl();
  const { data: memberData } = useMembers();
  const { data: invitationData } = useInvitations();
  const { data: currentUser } = useCurrentUser();
  const changeRole = useChangeRole();
  const removeMember = useRemoveMember();
  const resend = useResendInvitation();

  const isOwner = currentUser?.role === 'owner';
  const members = memberData?.members ?? [];
  const invitations = invitationData?.invitations ?? [];

  return (
    <div className="flex flex-col gap-8">
      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-[15px] font-semibold text-text-primary">
            {intl.formatMessage({ id: 'settings.members.heading' })}
          </h2>
          <InviteMemberModal
            trigger={
              <Button size="sm">{intl.formatMessage({ id: 'settings.members.invite' })}</Button>
            }
          />
        </div>
        <ul className="flex flex-col">
          {members.map((member) => (
            <li
              key={member.id}
              className="flex items-center gap-3 border-b border-divider py-2.5 last:border-b-0"
            >
              <Avatar
                size="sm"
                initials={member.initials}
                color={member.avatar_color}
                id={member.id}
              />
              <div className="min-w-0 flex-1">
                <div className="truncate text-[13px] font-medium text-text-primary">
                  {member.display_name ?? '—'}
                </div>
                <div className="truncate text-[11px] text-text-tertiary">{member.email}</div>
              </div>
              <RoleControl
                member={member}
                disabled={member.role === 'owner' || changeRole.isPending}
                onChange={(role) => changeRole.mutate({ userId: member.id, role })}
              />
              {isOwner && member.role !== 'owner' && member.id !== currentUser?.id ? (
                <ConfirmDialog
                  trigger={
                    <Button type="button" variant="ghost" size="sm">
                      {intl.formatMessage({ id: 'settings.members.remove' })}
                    </Button>
                  }
                  title={intl.formatMessage({ id: 'settings.members.removeTitle' })}
                  description={intl.formatMessage(
                    { id: 'settings.members.removeBody' },
                    { name: member.display_name ?? member.email },
                  )}
                  confirmLabel={intl.formatMessage({ id: 'settings.members.removeConfirm' })}
                  onConfirm={() => removeMember.mutateAsync(member.id)}
                  pending={removeMember.isPending}
                />
              ) : null}
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="mb-3 text-[15px] font-semibold text-text-primary">
          {intl.formatMessage({ id: 'settings.invitations.heading' })}
        </h2>
        {invitations.length === 0 ? (
          <p className="text-[13px] text-text-tertiary">
            {intl.formatMessage({ id: 'settings.invitations.empty' })}
          </p>
        ) : (
          <ul className="flex flex-col">
            {invitations.map((invitation) => (
              <InvitationRow
                key={invitation.id}
                invitation={invitation}
                onResend={() => resend.mutate(invitation.id)}
                resending={resend.isPending}
              />
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function RoleControl({
  member,
  disabled,
  onChange,
}: {
  member: Member;
  disabled: boolean;
  onChange: (role: 'admin' | 'member' | 'viewer') => void;
}) {
  const intl = useIntl();
  if (member.role === 'owner') {
    return (
      <span className="text-[13px] text-text-secondary">
        {intl.formatMessage({ id: 'role.owner' })}
      </span>
    );
  }
  return (
    <Select
      value={member.role}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value as 'admin' | 'member' | 'viewer')}
      aria-label={intl.formatMessage({ id: 'settings.members.role' })}
      className="w-32"
    >
      <option value="admin">{intl.formatMessage({ id: 'role.admin' })}</option>
      <option value="member">{intl.formatMessage({ id: 'role.member' })}</option>
      <option value="viewer">{intl.formatMessage({ id: 'role.viewer' })}</option>
    </Select>
  );
}

const STATUS_TONE: Record<Invitation['status'], string> = {
  pending: 'bg-status-todo-bg text-status-todo',
  accepted: 'bg-status-done-bg text-status-done',
  expired: 'bg-status-cancelled-bg text-status-cancelled',
};

function InvitationRow({
  invitation,
  onResend,
  resending,
}: {
  invitation: Invitation;
  onResend: () => void;
  resending: boolean;
}) {
  const intl = useIntl();
  return (
    <li className="flex items-center gap-3 border-b border-divider py-2.5 last:border-b-0">
      <div className="min-w-0 flex-1">
        <div className="truncate text-[13px] text-text-primary">{invitation.email}</div>
        <div className="text-[11px] text-text-tertiary">
          {intl.formatMessage({ id: `role.${invitation.role}` })} ·{' '}
          {formatRelativeTime(invitation.sent_at)}
        </div>
      </div>
      <span
        className={cn(
          'rounded-badge px-2 py-0.5 text-[11px] font-medium capitalize',
          STATUS_TONE[invitation.status],
        )}
      >
        {invitation.status}
      </span>
      {invitation.status !== 'accepted' ? (
        <Button type="button" variant="ghost" size="sm" onClick={onResend} disabled={resending}>
          {intl.formatMessage({ id: 'settings.invitations.resend' })}
        </Button>
      ) : null}
    </li>
  );
}
