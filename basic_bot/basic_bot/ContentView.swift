//
//  ContentView.swift
//  basic_bot
//
//  Created by Kristian Nelson on 2/25/25.
//

import SwiftUI

struct ContentView: View {
    @State private var userInput: String = ""
    @State private var botResponse: String = "Hello! How can I assist you today?"
    
    var body: some View {
        VStack {
            Text("BasicBot")
                .font(.largeTitle)
                .padding()
            
            ScrollView {
                Text(botResponse)
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(10)
                    .padding()
            }
            
            HStack {
                TextField("Type a message...", text: $userInput)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .padding()
                
                Button(action: sendMessage) {
                    Image(systemName: "paperplane.fill")
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .clipShape(Circle())
                }
                .padding()
            }
        }
    }
    
    func sendMessage() {
        guard !userInput.isEmpty else { return }
        
        let url = URL(string: "https://yourchatbot.com/chat")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body: [String: Any] = ["message": userInput]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body, options: [])
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let data = data, let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                DispatchQueue.main.async {
                    self.botResponse = json["response"] as? String ?? "Sorry, I didn't understand that."
                    self.userInput = "" // Clear input field after sending
                }
            }
        }.resume()
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}

