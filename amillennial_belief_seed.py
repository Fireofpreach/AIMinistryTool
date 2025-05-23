from app import app, db
from models import Denomination, Belief

# Detailed amillennial theological positions
amillennial_beliefs = [
    {
        "topic": "Eschatology (End Times)",
        "summary": "Amillennialism teaches that the thousand-year reign mentioned in Revelation 20 is symbolic, representing Christ's current reign in heaven and in the hearts of believers. The millennium is understood as the entire period between Christ's first and second comings. The church age is the fulfillment of God's kingdom promises.",
        "scripture_references": "Revelation 20:1-6, John 5:28-29, 2 Peter 3:10-13"
    },
    {
        "topic": "Kingdom of God",
        "summary": "The Kingdom of God is already present but not yet fully realized ('already-not yet'). It was inaugurated at Christ's first coming and will be consummated at His return. The church is the current manifestation of God's kingdom on earth.",
        "scripture_references": "Luke 17:20-21, Matthew 12:28, Colossians 1:13-14"
    },
    {
        "topic": "Israel and the Church",
        "summary": "The Church is the spiritual Israel, the fulfillment of God's promises to Abraham. The promises to ethnic Israel are ultimately fulfilled in Christ and the Church. The true Israel is not defined by ethnicity but by faith in Christ.",
        "scripture_references": "Romans 9:6-8, Galatians 3:7-9, Galatians 3:29, Romans 2:28-29"
    },
    {
        "topic": "The Rapture",
        "summary": "There is no separate rapture apart from the second coming of Christ. Believers who are alive at Christ's return will be caught up to meet Him in the air as He descends to earth for the final judgment.",
        "scripture_references": "1 Thessalonians 4:16-17, Matthew 24:31, 1 Corinthians 15:51-52"
    },
    {
        "topic": "The Tribulation",
        "summary": "The tribulation is not a future seven-year period, but represents the entire church age when believers face persecution. The church will endure tribulation until Christ's return.",
        "scripture_references": "John 16:33, Acts 14:22, Revelation 1:9"
    },
    {
        "topic": "The Antichrist",
        "summary": "The Antichrist is not necessarily a single future individual, but represents all powers and persons throughout history that oppose Christ and His church. There may be a final culmination of this antichrist spirit before Christ's return.",
        "scripture_references": "1 John 2:18, 2 Thessalonians 2:3-4, Revelation 13"
    },
    {
        "topic": "The Resurrection",
        "summary": "There will be a single bodily resurrection of all people (believers and unbelievers) at Christ's second coming, followed immediately by the final judgment.",
        "scripture_references": "John 5:28-29, Acts 24:15, Revelation 20:11-15"
    },
    {
        "topic": "The New Heavens and New Earth",
        "summary": "After Christ's return and the final judgment, God will create a new heavens and new earth—the eternal state where believers will dwell with God forever.",
        "scripture_references": "Revelation 21:1-4, 2 Peter 3:13, Isaiah 65:17"
    },
    {
        "topic": "Prophecy Interpretation",
        "summary": "Prophecy should be interpreted in light of its historical context, literary genre, and the progressive nature of revelation. Many Old Testament prophecies are fulfilled spiritually or typologically in Christ and the Church rather than literally with national Israel.",
        "scripture_references": "Hebrews 1:1-2, 1 Peter 1:10-12, Luke 24:25-27"
    }
]

def add_amillennial_denomination():
    """Add the Amillennial denomination and its detailed beliefs to the database"""
    with app.app_context():
        # Check if Amillennial denomination already exists
        amillennial = Denomination.query.filter_by(name="Amillennial").first()
        
        if not amillennial:
            # Create Amillennial denomination
            amillennial = Denomination(
                name="Amillennial",
                description="The foundational theological perspective that views the thousand-year reign mentioned in Revelation 20 as symbolic of Christ's current reign. Focuses on 'inaugurated eschatology' where God's kingdom is already present but not yet fully realized."
            )
            db.session.add(amillennial)
            db.session.commit()
            
            # Add detailed amillennial theological beliefs
            for belief_data in amillennial_beliefs:
                belief = Belief(
                    topic=belief_data["topic"],
                    summary=belief_data["summary"],
                    scripture_references=belief_data["scripture_references"],
                    denomination_id=amillennial.id
                )
                db.session.add(belief)
            
            db.session.commit()
            print("Amillennial denomination and beliefs added successfully!")
        else:
            print("Amillennial denomination already exists.")
            
            # Check if we need to add more beliefs
            existing_topics = [belief.topic for belief in Belief.query.filter_by(denomination_id=amillennial.id).all()]
            
            for belief_data in amillennial_beliefs:
                if belief_data["topic"] not in existing_topics:
                    belief = Belief(
                        topic=belief_data["topic"],
                        summary=belief_data["summary"],
                        scripture_references=belief_data["scripture_references"],
                        denomination_id=amillennial.id
                    )
                    db.session.add(belief)
            
            db.session.commit()
            print("Amillennial beliefs updated successfully!")

if __name__ == "__main__":
    add_amillennial_denomination()