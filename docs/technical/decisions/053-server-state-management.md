# Decision 053: Server State Management

**Status:** Decided

**Category:** Client Architecture

**Question:** How does the client fetch, cache, and invalidate server data?

**Options considered:**
- TanStack Query
- SWR
- RTK Query
- Apollo Client (not applicable — REST, not GraphQL)

**Decision:** TanStack Query v5.

- Every REST call goes through `useQuery` or `useMutation`.
- Cache keys follow a consistent hierarchy (`['workspace', workspaceId, 'projects', projectId, 'tasks']`).
- WebSocket events (Decision 045) drive either `queryClient.invalidateQueries(...)` for list-level changes or `queryClient.setQueryData(...)` for precise surgical updates to known entities.
- Optimistic drag-and-drop (Decision 046) uses TanStack Query's `onMutate` / `onError` / `onSettled`.

**Rationale:** TanStack Query is the standard for React + REST. Integrates cleanly with the WebSocket invalidation pattern. Provides background refetching, stale-while-revalidate, and request deduplication out of the box.
