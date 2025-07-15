import React, { useState, useEffect } from "react";
import "./App.css";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface SpotifyUser {
	id: string;
	display_name: string;
	email?: string;
	followers: number;
	images?: Array<{ url: string; height: number; width: number }>;
}

interface ChatMessage {
	id: string;
	content: string;
	role: "user" | "assistant";
	timestamp: Date;
}

function App() {
	const [isAuthenticated, setIsAuthenticated] = useState(false);
	const [isLoading, setIsLoading] = useState(true);
	const [user, setUser] = useState<SpotifyUser | null>(null);
	const [messages, setMessages] = useState<ChatMessage[]>([]);
	const [inputValue, setInputValue] = useState("");
	const [isTyping, setIsTyping] = useState(false);

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
			setMessages([]);
		} catch (error) {
			console.error("Error logging out:", error);
		}
	};

	const handleSendMessage = async (e: React.FormEvent) => {
		e.preventDefault();
		if (!inputValue.trim()) return;

		const userMessage: ChatMessage = {
			id: Date.now().toString(),
			content: inputValue,
			role: "user",
			timestamp: new Date(),
		};

		setMessages((prev) => [...prev, userMessage]);
		setInputValue("");
		setIsTyping(true);

		try {
			const response = await fetch("http://localhost:8080/chat", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ message: inputValue }),
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();

			const aiMessage: ChatMessage = {
				id: (Date.now() + 1).toString(),
				content: data.response || "Sorry, I couldn't process your request.",
				role: "assistant",
				timestamp: new Date(),
			};

			setMessages((prev) => [...prev, aiMessage]);
		} catch (error) {
			console.error("Error sending message:", error);
			const errorMessage: ChatMessage = {
				id: (Date.now() + 1).toString(),
				content:
					"Sorry, there was an error processing your request. Please try again.",
				role: "assistant",
				timestamp: new Date(),
			};
			setMessages((prev) => [...prev, errorMessage]);
		} finally {
			setIsTyping(false);
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
			<div className="sticky top-0 z-50 bg-black">
				<div className="container mx-auto px-4 py-5 flex justify-between items-center">
					<h1 className="text-2xl pinyon-script-regular">Personal Music Bot</h1>
					<div className="flex items-center space-x-4">
						{user && (
							<div className="flex items-center space-x-3">
								<Avatar className="h-8 w-8 border border-white/20">
									<AvatarImage
										src={
											user.images && user.images.length > 0
												? user.images[0].url
												: undefined
										}
										alt={user.display_name || user.id}
									/>
									<AvatarFallback className="bg-white/10 text-white text-xs adamina-regular">
										{(user.display_name || user.id).charAt(0).toUpperCase()}
									</AvatarFallback>
								</Avatar>
								<span className="text-sm adamina-regular">
									Welcome, {user.display_name || user.id}!
								</span>
							</div>
						)}
						<Button
							onClick={handleLogout}
							variant="outline"
							className="border-white adamina-regular text-black hover:shadow-[2px_2px_0_white] hover:translate-x-[-1px] hover:translate-y-[-1px]"
						>
							Logout
						</Button>
					</div>
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
				{messages.length === 0 ? (
					<div className="text-center text-white/50 adamina-regular mt-8">
						Start a conversation by asking about music, playlists, or
						recommendations!
					</div>
				) : (
					messages.map((message) => (
						<div
							key={message.id}
							className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
						>
							<div
								className={`max-w-[70%] p-4 rounded-lg adamina-regular text-sm ${
									message.role === "user"
										? "bg-white text-black ml-4"
										: "bg-white/10 text-white  mr-4"
								}`}
							>
								<div className="whitespace-pre-wrap">{message.content}</div>
								<div className="text-xs opacity-60 mt-2">
									{message.timestamp.toLocaleTimeString()}
								</div>
							</div>
						</div>
					))
				)}

				{isTyping && (
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
				)}
			</div>

			{/* Sticky input box at the bottom */}
			<div className="sticky adamina-regular bottom-0 left-0 w-full bg-black z-50">
				<form
					onSubmit={handleSendMessage}
					className="container mx-auto px-4 py-4 max-w-4xl flex space-x-2"
				>
					<Input
						type="text"
						placeholder="Ask about music, playlists, or get recommendations..."
						value={inputValue}
						onChange={(e) => setInputValue(e.target.value)}
						className="flex-1 bg-black border-white text-white placeholder:text-white/50 focus:border-white focus:ring-white/50"
						disabled={isTyping}
					/>
					<Button
						type="submit"
						variant="outline"
						className="border-white text-black hover:shadow-[2px_2px_0_white] hover:translate-x-[-1px] hover:translate-y-[-1px] disabled:opacity-50"
						disabled={isTyping || !inputValue.trim()}
					>
						Send
					</Button>
				</form>
			</div>
		</div>
	);
}
export default App;
