import React from "react";

export const TypingIndicator: React.FC = () => {
	return (
		<div className="flex justify-start">
			<div className="max-w-[70%] p-4 rounded-lg bg-white/10 text-white mr-4 adamina-regular">
				<div className="flex items-center space-x-2">
					<div className="flex space-x-1">
						<div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
						<div className="w-2 h-2 bg-white rounded-full animate-pulse animation-delay-75"></div>
						<div className="w-2 h-2 bg-white rounded-full animate-pulse animation-delay-150"></div>
					</div>
					<span className="text-white/60 text-sm">Typing...</span>
				</div>
			</div>
		</div>
	);
};
