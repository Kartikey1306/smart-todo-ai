-- Insert sample user
INSERT INTO users (email, name) VALUES 
('demo@example.com', 'Demo User')
ON CONFLICT (email) DO NOTHING;

-- Insert sample context entries to give the AI something to analyze
INSERT INTO context_entries (user_id, content, entry_type, entry_date) VALUES 
(1, 'Meeting with client about project deadline next Friday. They are concerned about the timeline.', 'meeting', CURRENT_DATE),
(1, 'Email from boss: "The quarterly review is coming up. Please prepare your presentation slides and gather performance metrics."', 'email', CURRENT_DATE),
(1, 'Note to self: Need to plan the team offsite event for next month. Must book a venue and send out invites.', 'note', CURRENT_DATE),
(1, 'Message from team lead: "The new feature deployment is blocked until you complete the code review for PR #123. Please get this done by Thursday."', 'message', CURRENT_DATE - INTERVAL '1 day'),
(1, 'Reminder: Annual dentist appointment is next week. Need to confirm the time.', 'note', CURRENT_DATE - INTERVAL '2 days');

-- Insert sample tasks with varying priorities, statuses, and deadlines
INSERT INTO tasks (user_id, title, description, priority, status, deadline, context_tags) VALUES 
(1, 'Prepare quarterly review presentation', 'Create slides and gather performance metrics for the upcoming review with management.', 1, 'pending', CURRENT_TIMESTAMP + INTERVAL '3 days', ARRAY['work', 'presentation', 'report']),
(1, 'Complete code review for PR #123', 'Review pull request from team members to unblock the feature deployment.', 1, 'in_progress', CURRENT_TIMESTAMP + INTERVAL '1 day', ARRAY['development', 'team', 'urgent']),
(1, 'Book venue for team offsite', 'Research and book a suitable venue for the Q3 team offsite event.', 2, 'pending', CURRENT_TIMESTAMP + INTERVAL '10 days', ARRAY['work', 'planning', 'event']),
(1, 'Buy groceries', 'Weekly grocery shopping for essentials.', 3, 'pending', CURRENT_TIMESTAMP + INTERVAL '2 days', ARRAY['personal', 'shopping']),
(1, 'Confirm dentist appointment', 'Call the clinic to confirm the time for the annual checkup.', 3, 'pending', CURRENT_TIMESTAMP + INTERVAL '4 days', ARRAY['health', 'personal', 'appointment']),
(1, 'Update project documentation', 'Update the API docs and user guides with the latest changes.', 2, 'completed', CURRENT_TIMESTAMP - INTERVAL '5 days', ARRAY['work', 'documentation']);
