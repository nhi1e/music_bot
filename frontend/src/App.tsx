import React, { useState, useEffect } from "react";
import "./App.css";

interface SpotifyUser {
	id: string;
	display_name: string;
	email?: string;
	followers: number;
	images?: Array<{ url: string; height: number; width: number }>;
}

function App() {
	const [isAuthenticated, setIsAuthenticated] = useState(false);
	const [isLoading, setIsLoading] = useState(true);
	const [user, setUser] = useState<SpotifyUser | null>(null);

	useEffect(() => {
		const checkAuth = async () => {
			// Check for auth callback parameters in URL
			const urlParams = new URLSearchParams(window.location.search);
			const authStatus = urlParams.get("auth");
			const username = urlParams.get("user");
			const errorMessage = urlParams.get("message");

			if (authStatus === "success") {
				// Clear URL parameters
				window.history.replaceState({}, document.title, "/");
				setIsAuthenticated(true);
				setIsLoading(false);
				return;
			}

			if (authStatus === "error") {
				// Clear URL parameters
				window.history.replaceState({}, document.title, "/");
				alert(
					`Authentication failed: ${decodeURIComponent(errorMessage || "Unknown error")}`
				);
				setIsLoading(false);
				return;
			}

			if (authStatus === "denied") {
				// Clear URL parameters
				window.history.replaceState({}, document.title, "/");
				alert("You denied access to Spotify. Please try again.");
				setIsLoading(false);
				return;
			}

			// Check if user is already authenticated via API
			try {
				const response = await fetch("http://localhost:8080/auth/status");
				const data = await response.json();
				setIsAuthenticated(data.authenticated);
				if (data.authenticated && data.user) {
					setUser(data.user);
				}
			} catch (error) {
				console.error("Error checking auth status:", error);
				setIsAuthenticated(false);
			}

			setIsLoading(false);
		};

		checkAuth();
	}, []);

	const handleSpotifyLogin = () => {
		const backendUrl = "http://localhost:8080";
		window.location.href = `${backendUrl}/auth/spotify`;
	};

	const handleLogout = async () => {
		try {
			await fetch("http://localhost:8080/auth/logout", { method: "POST" });
			setIsAuthenticated(false);
			setUser(null);
		} catch (error) {
			console.error("Error logging out:", error);
		}
	};
	const asciiBackground = String.raw`
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠤⠤⣄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⠉⢀⣀⣀⣿⣧⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣾⠁⣠⠖⠉⢀⣀⣧⣈⣧⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣷⣄⠀⠀⠀⠀⠀⠀⣠⢾⠛⣿⡁⣠⠞⠉⢀⣯⣀⣈⣇⠀
⠀⠀⠀⠀⠀⢀⣼⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠞⠉⠀⣀⣘⣏⠛⣷⢤⣀⣀⡤⠞⠁⣸⠟⠀⡷⠃⣠⣶⣟⣏⣀⣀⣘⣆
⠀⠀⠀⠀⠀⣾⡿⠛⢻⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠞⠀⣠⠖⠉⠉⠉⣏⠙⡿⢾⣄⣀⣀⣠⣼⣽⣠⠞⠀⡰⠃⢨⠟⠋⠀⠀⠀⠉
⠀⠀⠀⠀⢰⣿⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡏⢠⠞⠁⣠⣴⣾⣿⠏⠉⠓⢾⣦⣀⡀⢻⡿⠟⠁⢀⠞⠁⡴⠃⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠸⡇⠀⢀⣾⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣆⠀⡸⢀⠏⢠⠞⠁⣨⠟⠋⠉⠉⠉⢻⡧⢤⣈⣁⣀⣠⠖⠋⢀⡞⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣿⣤⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠛⢳⡇⡸⢠⠏⢠⠞⠁⣠⠔⠊⠉⠉⢻⠗⠦⣄⣀⠀⢀⣠⠔⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣠⣾⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⢠⣀⣀⣤⠀⠀⠀⠀⠀⠀⢸⣀⡞⣷⠇⡜⢠⠏⢀⡞⠁⠀⠀⣰⢞⣻⠇⠀⠀⠀⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣠⣾⣿⡿⣏⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡐⠦⠤⢤⡈⣻⢿⡖⠦⠤⣀⣠⣴⠏⢘⡟⢀⠃⡜⢠⠏⠀⠀⠀⠀⠛⠛⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⣴⣿⡿⠋⠀⢻⡉⠀⠀⠀⠀⠀⠀⠀⠀⠑⠒⠢⠄⢤⣀⣏⠙⢻⠲⠤⢿⣿⣋⠤⠊⢀⣾⣠⠃⡜⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢰⣿⡟⠀⢀⣴⣿⣿⣿⣿⣦⠀⠀⠀⠀⠀⠒⠒⠲⠤⣤⡀⣯⣉⠛⠒⠦⠤⣀⣀⣀⡤⠚⢹⣿⣰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢸⡿⠀⠀⣿⠟⠛⣿⠟⠛⣿⣧⠀⠀⠀⠐⠐⠒⠒⠰⣹⠷⣯⣈⡉⠑⠒⠦⠤⣀⣀⣀⡤⢿⢀⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠘⣿⡀⠀⢿⡀⠀⢻⣤⠖⢻⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠓⠲⠤⢄⣀⣀⣀⣼⠟⣸⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠘⢷⣄⠈⠙⠦⠸⡇⢀⡾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠙⠛⠶⠤⠶⣿⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢹⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢀⣴⣾⣿⣆⠀⠈⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠈⣿⣿⡿⠃⠀⣰⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⣙⠓⠒⠚⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    `;

	if (isLoading) {
		return (
			<div className="min-h-screen bg-black flex items-center justify-center">
				<div className="h-8 w-8 border-2 border-white border-b-transparent rounded-full animate-spin"></div>
			</div>
		);
	}

	if (!isAuthenticated) {
		return (
			<div className="relative min-h-screen bg-black flex items-center justify-center px-4 overflow-hidden">
				<pre className="absolute inset-0 text-white text-[20px] leading-none pointer-events-none z-0 select-none p-2 whitespace-pre-wrap">
					{asciiBackground}
				</pre>
				<div className="w-full max-w-sm text-white text-center space-y-6">
					<h1 className="text-7xl pinyon-script-regular">Personal Music Bot</h1>
					<button
						onClick={handleSpotifyLogin}
						className="w-full bg-black border border-white text-white adamina-regular font-semibold py-4 px-6 transition-all duration-200 transform flex items-center justify-center space-x-3 hover:shadow-[4px_4px_0_white] hover:translate-x-[-1px] hover:translate-y-[-1px]"
					>
						Continue with Spotify
					</button>
				</div>
			</div>
		);
	}

	return (
		<div className="min-h-screen bg-black text-white">
			<div className="container mx-auto px-4 py-8">
				{/* Header */}
				<div className="flex justify-between items-center mb-8">
					<h1 className="text-2xl pinyon-script-regular">Personal Music Bot</h1>
					<div className="flex items-center space-x-4">
						{user && (
							<span className="text-sm adamina-regular">
								Welcome, {user.display_name || user.id}!
							</span>
						)}
						<button
							onClick={handleLogout}
							className="bg-black border border-white text-white adamina-regular px-4 py-2 transition-all duration-200 hover:shadow-[2px_2px_0_white] hover:translate-x-[-1px] hover:translate-y-[-1px]"
						>
							Logout
						</button>
					</div>
				</div>

				{/* Chat interface */}
				<div className="max-w-4xl mx-auto">
					<div className="bg-black border border-white p-6 mb-4">
						<h2 className="text-xl adamina-regular mb-4">
							🎵 Ready to discover amazing music!
						</h2>
						<p className="text-gray-300 mb-4">
							Ask me about your music preferences, get recommendations, or chat
							about your favorite artists!
						</p>
						<div className="space-y-2">
							<p className="text-sm text-gray-400">Try asking:</p>
							<ul className="text-sm text-gray-400 space-y-1 ml-4">
								<li>• "What are my top tracks?"</li>
								<li>• "Recommend music similar to [artist]"</li>
								<li>• "Find new music based on my taste"</li>
							</ul>
						</div>
					</div>

					{/* Simple chat input for now */}
					<div className="flex space-x-2">
						<input
							type="text"
							placeholder="Ask me about music..."
							className="flex-1 bg-black border border-white text-white p-3 adamina-regular focus:outline-none focus:shadow-[2px_2px_0_white]"
						/>
						<button className="bg-black border border-white text-white adamina-regular px-6 py-3 transition-all duration-200 hover:shadow-[2px_2px_0_white] hover:translate-x-[-1px] hover:translate-y-[-1px]">
							Send
						</button>
					</div>
				</div>
			</div>
		</div>
	);
}

export default App;
