import React, { useState, useEffect } from "react";
import "./App.css";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";


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
  const chatAsciiBackground = String.raw`
  ⠀⠀⠀⠀⣠⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⡇⠀⠀⠀⠘⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣼⣿⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡼⣡⣇⠀⠀⠀⠀⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢠⣿⣿⠟⢻⣿⠤⠖⠒⠚⠉⠉⠉⠉⠉⠉⢩⡟⣹⠋⣿⠉⠉⠛⠒⣺⡤⢄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢸⣿⡟⠀⢠⣿⡇⠀⢀⡄⠀⠀⠀⠀⠀⠀⣏⣼⣃⣠⣽⡤⠤⢴⠯⣭⠧⢼⣎⡳⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠈⣿⡇⠀⣼⣿⡇⠀⠰⣇⣠⡤⠴⠒⠚⠉⣿⠁⣤⣾⣿⡇⢀⣈⣉⣥⡤⢼⠬⣯⣛⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡄⠀⠀⠀⠀⠀
⠀⠀⠀⢻⣧⣼⣿⣿⠧⠒⠋⣏⣄⠀⠀⠀⠀⠀⢹⣀⡿⠿⠛⠉⠉⠁⠀⣀⣴⣾⠾⠓⠲⡯⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣞⣇⠀⠀⠀⠀⠀
⠀⠀⠀⣠⣿⣿⣿⡟⠀⠀⠀⣇⡿⠃⣀⡤⠴⠚⢹⡇⠀⠀⣀⡠⠖⠚⠉⢀⣀⠤⠖⠚⣹⣋⣏⡟⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⢯⠏⢿⠀⠀⣄⠀⠀
⠀⠀⣴⣿⣿⣿⡟⠀⠀⠀⢀⡫⠖⠋⠁⠀⠀⣠⣤⣧⠴⠋⠁⠀⣀⡤⠚⠉⠀⠀⠀⣰⠃⡽⠣⣏⡧⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⠀⢸⣧⣴⣾⣀⠀⢸⡀⠀
⢀⣾⣿⣿⡿⢻⣷⢀⡤⠞⠉⠀⠀⠀⠀⢀⣼⣿⡿⠏⠀⣀⡴⠛⠁⠀⠀⠀⠀⢀⡴⠁⡴⠁⡼⢸⣷⢸⠀⠀⠀⠀⠈⣧⠀⠀⠀⣀⡠⠔⠚⠉⠁⠀⠀⠀⠈⡇⠉⠁⠀⠉⣑⣧⢄
⣼⣿⣿⠟⠀⣨⣿⣿⣿⣷⣦⡀⢀⣠⠖⠋⠀⠀⢀⣤⠞⠁⠀⠀⠀⠀⠀⣦⣠⠞⢶⡞⠣⣼⢁⡼⢁⡏⠀⠀⠀⠀⠀⢘⣧⠔⠋⠁⢀⡀⣀⡠⠴⠒⠚⢩⣽⡯⠉⠉⠉⠙⠷⠞⠤
⣿⣿⡏⠀⣾⣿⣿⣿⡿⢿⣿⣿⣏⠁⠀⠀⢠⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⢰⠛⢦⠎⢉⠿⣌⡞⢀⡞⠀⠀⠀⢀⡤⠚⠉⠘⣇⣀⠤⠚⣯⠁⠀⠀⣀⣤⠼⠟⠓⠒⠒⠒⠒⢓⠒⠒
⣿⣿⡇⠰⣿⣿⠁⢻⣧⠀⠹⣿⣿⠀⣠⠞⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⢠⢯⣷⡏⢰⢿⢇⠞⠀⣀⠴⠚⠁⠀⢀⣠⡶⢻⡇⠀⢀⡸⡶⠚⠉⠀⢸⡓⣦⣠⠤⠤⠒⠒⢺⡂⢉
⠘⣿⣇⠀⢻⣿⣄⠈⣿⡆⠀⣿⣿⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠱⣮⣸⣋⣰⣋⣤⠾⠒⠉⠀⣠⣆⡠⠖⠋⠹⠤⣞⠴⠚⠁⠀⢻⣀⡤⠖⠊⡏⢸⠇⠀⣀⠤⠔⠺⠟⠈
⠀⠘⢿⣷⣄⡈⠛⠛⢸⣿⣾⡿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢾⣠⠇⢠⠋⠀⣀⣠⣾⡟⡏⠀⠀⣀⠴⠊⠁⠀⢀⡠⣶⣿⡇⠀⢀⣴⣾⠼⠚⠉⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⠙⠛⠿⠿⠟⢻⣯⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢾⢉⠏⠉⠉⠁⣻⢋⣤⡧⠴⠋⢷⡀⢀⡤⠚⠉⠀⠿⠿⣃⠴⠚⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⣀⡀⠀⠈⣿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣽⠒⠠⠤⠔⣿⠛⠛⠁⠀⣀⡬⢿⠁⠀⠀⠀⣀⡴⠚⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣰⣿⣿⣿⣆⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⠦⣀⣀⣤⣿⣀⡠⠴⠊⠁⠀⢈⣧⣀⠴⠚⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢻⣿⣿⣿⠟⢀⣼⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⡀⠈⠉⠁⠀⠀⠀⠀⢀⣠⡿⣻⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠈⠛⠿⠿⠿⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠒⠲⠦⠶⠒⠚⠉⠁⠀⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
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
		<div className="min-h-screen bg-black text-white flex flex-col font-mono">
			{/* Header */}
			<div className="container mx-auto px-4 py-6 flex justify-between items-center">
				<h1 className="text-2xl pinyon-script-regular">Personal Music Bot</h1>
				<div className="flex items-center space-x-4">
					{user && (
						<span className="text-sm adamina-regular">
							Welcome, {user.display_name || user.id}!
						</span>
					)}
					<Button
						type="submit"
						variant="outline"
						className="border-white adamina-regular text-black hover:shadow-[2px_2px_0_white] hover:translate-x-[-1px] hover:translate-y-[-1px]"
					>
						Logout
					</Button>
				</div>
			</div>
			{/* ASCII Background */}
			<div className="relative w-full flex flex-col items-center text-center">
				<pre className="text-white/50 text-[10px] leading-none select-none whitespace-pre-wrap px-2">
					{chatAsciiBackground}
				</pre>
			</div>

			{/* Catchphrase */}
			<div className="text-center mb-4">
				<h2 className="text-xl font-semibold text-white adamina-regular">
					what’s on the playlist today?
				</h2>
			</div>

			{/* Chat content (scrollable area) */}
			<div className="flex-1 overflow-y-auto px-4 pb-32 container mx-auto max-w-4xl space-y-4">
				{/* Example chat messages */}

				{/* Add more chat messages dynamically here */}
			</div>

			{/* Sticky input box at the bottom */}
			<div className="sticky adamina-regular bottom-0 left-0 w-full bg-black  z-50">
				<div className="container mx-auto px-4 py-4 max-w-4xl flex space-x-2">
					<Input type="email" placeholder="Ask something" />
					<Button
						type="submit"
						variant="outline"
						className="border-white text-black hover:shadow-[2px_2px_0_white] hover:translate-x-[-1px] hover:translate-y-[-1px]"
					>
						Send
					</Button>
				</div>
			</div>
		</div>
	);
  
}
export default App;
