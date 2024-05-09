//
//  SettingsView.swift
//  MyApp
//
//  Created by Example Dev on 05.05.24.
//

import SwiftUI

struct SettingsView: View {
    @State private var notificationsEnabled = false
    @State private var locationAccess = false
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("Preferences")) {
                    Toggle(isOn: $notificationsEnabled) {
                        Text("Enable Notifications")
                    }
                    Toggle(isOn: $locationAccess) {
                        Text("Location Access")
                    }
                }
                
                Section(header: Text("About")) {
                    Text("Version 1.0.3")
                    Text("Terms of Service")
                    Text("Privacy Policy")
                }
            }
            .navigationBarTitle("Settings")
        }
    }
}

struct SettingsView_Previews: PreviewProvider {
    static var previews: some View {
        SettingsView()
    }
}
