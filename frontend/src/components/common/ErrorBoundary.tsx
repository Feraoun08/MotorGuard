import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface ErrorBoundaryProps {
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
}

export default class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);

    this.state = {
      hasError: false,
    };
  }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return {
      hasError: true,
    };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("MotorGuard frontend rendering error:", error);
    console.error("Component stack:", info.componentStack);
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="app-error-boundary">
          <div className="app-error-card">
            <div className="app-error-icon">
              <AlertTriangle size={30} />
            </div>

            <h1>Something went wrong</h1>

            <p>
              MotorGuard encountered an unexpected interface error.
              You can reload the application to try again.
            </p>

            <button
              onClick={this.handleReload}
              className="app-error-reload"
            >
              <RefreshCw size={16} />
              Reload application
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}