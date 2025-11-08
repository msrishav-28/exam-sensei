'use client'

import { useState, useEffect } from 'react'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'

interface ExamEvent {
  id: string
  title: string
  start: string
  end?: string
  backgroundColor: string
  extendedProps: {
    examCode: string
    type: string
    description: string
  }
}

export default function CalendarPage() {
  const [events, setEvents] = useState<ExamEvent[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchExamEvents()
  }, [])

  const fetchExamEvents = async () => {
    try {
      // Fetch exams from API
      const response = await fetch('http://localhost:8000/exams/')
      const exams = await response.json()

      // Convert exams to calendar events
      const calendarEvents: ExamEvent[] = []

      exams.forEach((exam: any) => {
        if (exam.important_dates) {
          const dates = typeof exam.important_dates === 'string'
            ? JSON.parse(exam.important_dates)
            : exam.important_dates

          // Add notification dates
          if (dates.notification) {
            calendarEvents.push({
              id: `${exam.code}_notification`,
              title: `${exam.name} - Notification`,
              start: dates.notification,
              backgroundColor: '#3B82F6', // blue
              extendedProps: {
                examCode: exam.code,
                type: 'notification',
                description: 'Application notification released'
              }
            })
          }

          // Add application dates
          if (dates.application_start) {
            calendarEvents.push({
              id: `${exam.code}_application_start`,
              title: `${exam.name} - Application Start`,
              start: dates.application_start,
              backgroundColor: '#10B981', // green
              extendedProps: {
                examCode: exam.code,
                type: 'application_start',
                description: 'Application period begins'
              }
            })
          }

          if (dates.application_end) {
            calendarEvents.push({
              id: `${exam.code}_application_end`,
              title: `${exam.name} - Application End`,
              start: dates.application_end,
              backgroundColor: '#EF4444', // red
              extendedProps: {
                examCode: exam.code,
                type: 'application_end',
                description: 'Last date to apply'
              }
            })
          }

          // Add exam dates
          if (dates.exam_dates && Array.isArray(dates.exam_dates)) {
            dates.exam_dates.forEach((examDate: string, index: number) => {
              calendarEvents.push({
                id: `${exam.code}_exam_${index}`,
                title: `${exam.name} - Exam`,
                start: examDate,
                backgroundColor: '#8B5CF6', // purple
                extendedProps: {
                  examCode: exam.code,
                  type: 'exam',
                  description: 'Examination date'
                }
              })
            })
          }

          // Add result dates
          if (dates.result) {
            calendarEvents.push({
              id: `${exam.code}_result`,
              title: `${exam.name} - Result`,
              start: dates.result,
              backgroundColor: '#F59E0B', // amber
              extendedProps: {
                examCode: exam.code,
                type: 'result',
                description: 'Results declared'
              }
            })
          }
        }
      })

      setEvents(calendarEvents)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching exam events:', error)
      setLoading(false)
    }
  }

  const handleEventClick = (info: any) => {
    const event = info.event
    const props = event.extendedProps

    alert(`${event.title}\n\n${props.description}\n\nExam Code: ${props.examCode}`)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading calendar...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">ExamSensei - Calendar</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => window.location.href = '/'}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-6">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">Exam Calendar</h2>
            <p className="text-gray-600">Track all important exam dates in one place</p>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <FullCalendar
              plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
              headerToolbar={{
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
              }}
              initialView="dayGridMonth"
              events={events}
              eventClick={handleEventClick}
              height="auto"
              eventDisplay="block"
              dayMaxEvents={3}
            />
          </div>

          <div className="mt-6 bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Legend</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-blue-500 rounded mr-2"></div>
                <span className="text-sm">Notification</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
                <span className="text-sm">Application Start</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 bg-red-500 rounded mr-2"></div>
                <span className="text-sm">Application End</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 bg-purple-500 rounded mr-2"></div>
                <span className="text-sm">Exam Date</span>
              </div>
              <div className="flex items-center">
                <div className="w-4 h-4 bg-yellow-500 rounded mr-2"></div>
                <span className="text-sm">Results</span>
              </div>
            </div>
          </div>

          <div className="mt-6 bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Upcoming Events</h3>
            <div className="space-y-4">
              {events
                .filter(event => new Date(event.start) >= new Date())
                .sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime())
                .slice(0, 5)
                .map(event => (
                  <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <div>
                      <p className="font-medium text-gray-900">{event.title}</p>
                      <p className="text-sm text-gray-600">{event.extendedProps.description}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        {new Date(event.start).toLocaleDateString()}
                      </p>
                      <p className="text-xs text-gray-500">
                        {Math.ceil((new Date(event.start).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))} days left
                      </p>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
