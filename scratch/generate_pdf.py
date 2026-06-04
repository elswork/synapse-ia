import os
from fpdf import FPDF

class EciPdf(FPDF):
    def header(self):
        # Color bar header
        self.set_fill_color(26, 36, 43)  # Dark Navy
        self.rect(0, 0, 210, 18, "F")
        self.set_fill_color(183, 121, 31)  # Warm Gold
        self.rect(0, 18, 210, 2, "F")
        
        # Header text
        self.set_xy(15, 4)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 10, "ANTIKYTHERA PROJECT | SOVEREIGN DIGITAL INFRASTRUCTURE", 0, 0, "L")
        self.ln(25)

    def footer(self):
        self.set_y(-20)
        # Gold footer separator line
        self.set_fill_color(183, 121, 31)
        self.rect(15, self.get_y(), 180, 0.5, "F")
        
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        # Left side: Date / Project name
        self.cell(90, 10, "Project Antikythera (https://anticitera.deft.work)", 0, 0, "L")
        # Right side: Page number
        self.cell(90, 10, f"Page {self.page_no()}", 0, 0, "R")

def create_pdf(output_path):
    pdf = EciPdf(orientation="P", unit="mm", format="A4")
    pdf.set_margins(20, 20, 20)
    pdf.add_page()
    
    # Title
    pdf.set_text_color(26, 36, 43)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "European Citizens' Initiative (ECI)", 0, 1, "L")
    
    # Subtitle
    pdf.set_text_color(183, 121, 31)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 6, "Call for Co-Organizers: Securing the .ia Domain", 0, 1, "L")
    pdf.ln(8)
    
    # Reset text color
    pdf.set_text_color(40, 40, 40)
    pdf.set_font("Helvetica", size=10.5)
    
    body_text_1 = (
        "We are preparing the official launch of a European Citizens' Initiative (ECI) "
        "to claim and protect the .ia (Augmented/Artificial Intelligence) top-level domain "
        "as a sovereign European public asset under the ISO 3166-1 \"Exceptional Reservation\" status."
    )
    
    body_text_2 = (
        "Our goal is to ensure that AI's core digital identifier remains under democratic "
        "European governance and GDPR standards, rather than being captured by opaque, "
        "speculative, or offshore private interests."
    )
    
    challenge_title = "The Challenge:"
    challenge_text = (
        "To register the ECI with the European Commission, we must form a Citizens' Committee "
        "composed of at least 7 EU citizens residing in 7 different EU Member States. We currently "
        "have members from Spain and France, and we are seeking 5 more co-organizers from other "
        "EU countries."
    )
    
    seeking_title = "Who We Are Looking For:"
    seeking_intro = (
        "We are looking for EU residents/citizens (e.g., from Germany, Italy, Poland, Ireland, "
        "Netherlands, Belgium, Sweden, Greece, etc.) who work or are interested in:"
    )
    
    profiles = [
        "Software Engineering / DevOps / Networking",
        "Digital Law / GDPR / Cyber-security",
        "AI Ethics & Regulation",
        "European Civic Tech"
    ]
    
    call_to_action_1 = (
        "If you want to join this legal-tech maneuver as a co-organizer and help us build a "
        "sovereign digital alternative, we would love to have you. This role requires minimal "
        "administrative overhead but carries maximum historical impact."
    )
    
    # Main Body
    pdf.write(5.5, "Hello everyone!\n\n")
    pdf.write(5.5, f"I'm writing on behalf of the Antikythera Project (https://anticitera.deft.work). {body_text_1}\n\n")
    pdf.write(5.5, f"{body_text_2}\n\n")
    
    # Challenge section
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(26, 36, 43)
    pdf.cell(0, 6, challenge_title, 0, 1, "L")
    pdf.set_font("Helvetica", size=10.5)
    pdf.set_text_color(40, 40, 40)
    pdf.write(5.5, f"{challenge_text}\n\n")
    
    # Seeking section
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(26, 36, 43)
    pdf.cell(0, 6, seeking_title, 0, 1, "L")
    pdf.set_font("Helvetica", size=10.5)
    pdf.set_text_color(40, 40, 40)
    pdf.write(5.5, f"{seeking_intro}\n\n")
    
    # Bullet points
    for profile in profiles:
        pdf.set_x(25)
        pdf.write(5.5, f"*  {profile}\n")
    pdf.ln(5)
    
    pdf.write(5.5, f"{call_to_action_1}\n\n")
    
    # Highlight Box / Link Section
    pdf.set_fill_color(245, 247, 250)
    # We want a subtle border
    pdf.set_draw_color(183, 121, 31)
    pdf.set_line_width(0.3)
    
    # Store current Y position
    start_y = pdf.get_y()
    box_height = 25
    pdf.rect(20, start_y, 170, box_height, "DF")
    
    pdf.set_xy(25, start_y + 3)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(183, 121, 31)
    pdf.cell(0, 6, "Do you want to join the Citizens' Committee?", 0, 1, "L")
    
    pdf.set_x(25)
    pdf.set_font("Helvetica", "U", 10.5)
    pdf.set_text_color(0, 0, 238)
    # Link
    pdf.cell(0, 6, "https://anticitera.deft.work/comite/", 0, 1, "L", link="https://anticitera.deft.work/comite/")
    
    # Restore Y pos below box
    pdf.set_xy(20, start_y + box_height + 5)
    
    # Contact and Footer
    pdf.set_font("Helvetica", size=10.5)
    pdf.set_text_color(40, 40, 40)
    pdf.write(5.5, "Feel free to DM me or reach out directly at elswork@gmail.com.\n\n")
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(26, 36, 43)
    pdf.write(5.5, "Let's build a sovereign digital future for Europe together! \n")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf.output(output_path)
    print(f"PDF generated successfully at: {output_path}")

if __name__ == "__main__":
    create_pdf("/home/pirate/docker/Arquimedes/agora/diplomacy/ICE/ECI_Outreach_Call.pdf")
