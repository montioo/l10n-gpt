//
//  SettingsView.swift
//  MyApp
//
//  Created by Example Dev on 05.05.24.
//

import SwiftUI

let example_multi_line = String(localized:"""
This is a string
with multiple lines

and some empty lines.
""", comment: "In swift code, this was a string that spans multiple lines.")

let example_line_breaks = String(
    localized: "This string contains\nnewline\n\ncharacters.",
    comment: "In swift code, this was a single line string containing newline characters.")

let example_with_quotes = String(
    localized: "This single line \"string\" contains quotes.",
    comment: "In swift code, this was a single line string containing escaped quotes."
)

let example_with_quotes2 = String(
    localized: """
We can \"escape\" quotes or just
"write" them.
""", comment: "In swift code, this was a multi line string containing quotes and escaped quotes."
)


struct SettingsView: View {
    @State private var notificationsEnabled = false
    @State private var locationAccess = false
    
    var body: some View {
        NavigationView {
            Form {
                let preferencesHeader = String(localized: "Preferences", comment: "Header for the preferences section in settings")
                Section(header: Text(preferencesHeader)) {
                    Toggle(isOn: $notificationsEnabled) {
                        Text(String(localized: "Enable Notifications", comment: "Toggle label for enabling notifications in settings"))
                    }
                    Toggle(isOn: $locationAccess) {
                        Text(String(localized: "Location Access", comment: "Toggle label for giving location access in settings"))
                    }
                }
                
                let aboutHeader = String(localized: "About", comment: "Header for the about section in settings")
                Section(header: Text(aboutHeader)) {
                    Text(String(localized: "Version 1.0.3", comment: "Label showing app version in settings"))
                    Text(String(localized: "Terms of Service", comment: "Label for terms of service in settings"))
                    Text(String(localized: "Privacy Policy", comment: "Label for privacy policy in settings"))
                    Text(example_multi_line)
                    Text(example_line_breaks)
                    Text(example_with_quotes)
                    Text(example_with_quotes2)
                }
            }
            .navigationBarTitle(Text(String(localized: "Settings", comment: "Navigation bar title for settings view")))
        }
    }
}

struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
    }
}


#Preview {
    SettingsView()
}
