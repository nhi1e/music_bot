import React from "react";

export const LoadingSpinner: React.FC = () => {
	return (
		<div className="min-h-screen bg-black flex items-center justify-center">
			<div className="h-8 w-8 border-2 border-white border-b-transparent rounded-full animate-spin"></div>
		</div>
	);
};
