/**
 * Bridge between the module-level QueryClient (constructed before React renders,
 * so it has no access to the toast context) and the React toast layer.
 *
 * The global MutationCache `onError` in `app/query-client.ts` calls
 * {@link notifyMutationError} for any mutation that opted in with
 * `meta: { errorToast: true }`. A listener mounted inside the providers
 * (`app/MutationErrorListener.tsx`) registers a handler that shows the
 * standardized error toast (DRD §18.2). Opt-in — not opt-out — because most
 * mutations already surface contextual inline errors (auth screens, form
 * modals) and a blanket toast would double up on them.
 */
type Handler = () => void;

let handler: Handler | null = null;

/** Register the toast-showing handler; returns an unsubscribe for cleanup. */
export function registerMutationErrorHandler(fn: Handler): () => void {
  handler = fn;
  return () => {
    if (handler === fn) handler = null;
  };
}

/** Invoke the registered handler, if any. No-op before the listener mounts. */
export function notifyMutationError(): void {
  handler?.();
}
