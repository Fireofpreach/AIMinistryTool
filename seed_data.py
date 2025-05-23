from app import app, db
from models import Denomination, Belief, User
from werkzeug.security import generate_password_hash

# List of denominations with descriptions
denominations = [
    {
        "name": "Roman Catholic",
        "description": "The largest Christian church, led by the Pope and with a history dating back almost 2,000 years."
    },
    {
        "name": "Eastern Orthodox",
        "description": "The second-largest Christian church, with a rich tradition of liturgy and spirituality."
    },
    {
        "name": "Lutheran",
        "description": "Protestant denomination originating from the teachings of Martin Luther in the 16th century."
    },
    {
        "name": "Baptist",
        "description": "Protestant denomination emphasizing believer's baptism and the autonomy of local churches."
    },
    {
        "name": "Methodist",
        "description": "Protestant denomination founded by John Wesley with an emphasis on sanctification and social justice."
    },
    {
        "name": "Presbyterian",
        "description": "Protestant denomination with roots in Calvinism and known for its representative form of church government."
    },
    {
        "name": "Anglican/Episcopal",
        "description": "Protestant denomination that maintains traditions and practices from both Catholic and Reformed theology."
    },
    {
        "name": "Pentecostal",
        "description": "Protestant denomination emphasizing the work of the Holy Spirit, spiritual gifts, and expressive worship."
    }
]

# List of theological topics and beliefs for each denomination
beliefs = [
    # Salvation
    {
        "topic": "Salvation",
        "denomination": "Roman Catholic",
        "summary": "Salvation involves both faith and good works, and comes through the Church's sacraments. Baptism removes original sin, and sanctifying grace is infused through the sacraments.",
        "scripture_references": "James 2:24, Matthew 19:16-17"
    },
    {
        "topic": "Salvation",
        "denomination": "Eastern Orthodox",
        "summary": "Salvation is a process of theosis (becoming like God), involving synergy between divine grace and human freedom. Sacraments are essential channels of grace.",
        "scripture_references": "2 Peter 1:4, Romans 8:29-30"
    },
    {
        "topic": "Salvation",
        "denomination": "Lutheran",
        "summary": "Salvation is by grace alone through faith alone in Christ alone. Good works are the result of salvation, not a means to it.",
        "scripture_references": "Ephesians 2:8-9, Romans 3:28"
    },
    {
        "topic": "Salvation",
        "denomination": "Baptist",
        "summary": "Salvation is by grace through faith alone, with emphasis on a personal conversion experience. Once saved, always saved (eternal security).",
        "scripture_references": "John 3:16, Romans 10:9-10"
    },
    {
        "topic": "Salvation",
        "denomination": "Methodist",
        "summary": "Salvation involves prevenient grace, justification by faith, and sanctification. Salvation can be lost through willful, persistent sin.",
        "scripture_references": "Philippians 2:12-13, Hebrews 6:4-6"
    },
    {
        "topic": "Salvation",
        "denomination": "Presbyterian",
        "summary": "Salvation is by grace alone through faith alone, with an emphasis on God's sovereignty and predestination. The elect are saved by God's unconditional choice.",
        "scripture_references": "Ephesians 1:4-5, Romans 8:28-30"
    },
    {
        "topic": "Salvation",
        "denomination": "Anglican/Episcopal",
        "summary": "Salvation is by grace through faith, with sacraments as means of grace. Tends to balance Catholic and Protestant views.",
        "scripture_references": "Ephesians 2:8-10, 1 Peter 3:21"
    },
    {
        "topic": "Salvation",
        "denomination": "Pentecostal",
        "summary": "Salvation is by grace through faith, often with emphasis on a definite conversion experience. Many also emphasize the baptism of the Holy Spirit as a subsequent experience.",
        "scripture_references": "Acts 2:38, Mark 16:16"
    },
    
    # Baptism
    {
        "topic": "Baptism",
        "denomination": "Roman Catholic",
        "summary": "Sacrament necessary for salvation that removes original sin. Typically performed on infants by sprinkling or pouring water.",
        "scripture_references": "John 3:5, Acts 2:38-39"
    },
    {
        "topic": "Baptism",
        "denomination": "Eastern Orthodox",
        "summary": "Essential sacrament that incorporates one into the Church. Performed by triple immersion, typically for infants.",
        "scripture_references": "Romans 6:3-4, Colossians 2:12"
    },
    {
        "topic": "Baptism",
        "denomination": "Lutheran",
        "summary": "Sacrament that creates faith and delivers God's grace. Typically performed on infants by sprinkling, pouring, or immersion.",
        "scripture_references": "Mark 16:16, 1 Peter 3:21"
    },
    {
        "topic": "Baptism",
        "denomination": "Baptist",
        "summary": "Ordinance (symbolic act) for believers only, performed by full immersion. Not necessary for salvation but a public profession of faith.",
        "scripture_references": "Acts 8:36-38, Matthew 28:19-20"
    },
    {
        "topic": "Baptism",
        "denomination": "Methodist",
        "summary": "Sacrament and means of grace, typically performed on infants by sprinkling or pouring, but also for adult converts.",
        "scripture_references": "Acts 16:15, Acts 16:33"
    },
    {
        "topic": "Baptism",
        "denomination": "Presbyterian",
        "summary": "Sign and seal of the covenant of grace, typically performed on infants of believers by sprinkling or pouring.",
        "scripture_references": "Genesis 17:7, Acts 2:39"
    },
    {
        "topic": "Baptism",
        "denomination": "Anglican/Episcopal",
        "summary": "Sacrament of initiation into the Church, typically performed on infants by sprinkling or pouring.",
        "scripture_references": "Acts 2:38-39, Titus 3:5"
    },
    {
        "topic": "Baptism",
        "denomination": "Pentecostal",
        "summary": "Ordinance for believers only, usually by immersion. Many distinguish between water baptism and baptism of the Holy Spirit.",
        "scripture_references": "Acts 2:38, Acts 8:12"
    },
    
    # Scripture and Authority
    {
        "topic": "Scripture and Authority",
        "denomination": "Roman Catholic",
        "summary": "Scripture and Tradition are equal authorities. The Magisterium (teaching office of the Church) interprets both authoritatively.",
        "scripture_references": "2 Thessalonians 2:15, 1 Timothy 3:15"
    },
    {
        "topic": "Scripture and Authority",
        "denomination": "Eastern Orthodox",
        "summary": "Scripture is interpreted within Holy Tradition, which includes the ecumenical councils, writings of Church Fathers, liturgy, and icons.",
        "scripture_references": "2 Thessalonians 2:15, 2 Timothy 2:2"
    },
    {
        "topic": "Scripture and Authority",
        "denomination": "Lutheran",
        "summary": "Scripture alone (sola scriptura) is the ultimate authority. Tradition is valuable but subordinate to Scripture.",
        "scripture_references": "2 Timothy 3:16-17, Isaiah 8:20"
    },
    {
        "topic": "Scripture and Authority",
        "denomination": "Baptist",
        "summary": "Scripture alone is the final authority for faith and practice. Emphasizes the individual's right to interpret Scripture guided by the Holy Spirit.",
        "scripture_references": "2 Timothy 3:16-17, 2 Peter 1:20-21"
    },
    {
        "topic": "Scripture and Authority",
        "denomination": "Methodist",
        "summary": "Scripture is the primary authority, interpreted through tradition, reason, and experience (the Wesleyan Quadrilateral).",
        "scripture_references": "2 Timothy 3:16-17, Acts 15:28"
    },
    {
        "topic": "Scripture and Authority",
        "denomination": "Presbyterian",
        "summary": "Scripture alone is the ultimate authority. Creeds and confessions are important subordinate standards.",
        "scripture_references": "2 Timothy 3:16-17, 2 Peter 1:20-21"
    },
    {
        "topic": "Scripture and Authority",
        "denomination": "Anglican/Episcopal",
        "summary": "Scripture contains all things necessary for salvation. Tradition and reason help interpret Scripture (the three-legged stool).",
        "scripture_references": "2 Timothy 3:16-17, John 20:31"
    },
    {
        "topic": "Scripture and Authority",
        "denomination": "Pentecostal",
        "summary": "Scripture is the inspired and authoritative Word of God. Emphasis on the Holy Spirit's ongoing revelation, though subordinate to Scripture.",
        "scripture_references": "2 Timothy 3:16-17, Joel 2:28-29"
    },
    
    # Communion/Eucharist
    {
        "topic": "Communion/Eucharist",
        "denomination": "Roman Catholic",
        "summary": "Transubstantiation: the bread and wine become the actual body and blood of Christ. The Mass is a sacrifice re-presenting Christ's sacrifice.",
        "scripture_references": "John 6:53-58, 1 Corinthians 11:23-29"
    },
    {
        "topic": "Communion/Eucharist",
        "denomination": "Eastern Orthodox",
        "summary": "The bread and wine truly become the body and blood of Christ through mystery. The Divine Liturgy makes present Christ's sacrifice.",
        "scripture_references": "John 6:53-58, 1 Corinthians 10:16-17"
    },
    {
        "topic": "Communion/Eucharist",
        "denomination": "Lutheran",
        "summary": "Consubstantiation or Sacramental Union: Christ is truly present in, with, and under the elements, though they remain bread and wine.",
        "scripture_references": "1 Corinthians 11:23-29, Matthew 26:26-28"
    },
    {
        "topic": "Communion/Eucharist",
        "denomination": "Baptist",
        "summary": "Memorial view: the bread and wine are symbols commemorating Christ's death. The Lord's Supper is an ordinance for believers only.",
        "scripture_references": "1 Corinthians 11:24-26, Luke 22:19"
    },
    {
        "topic": "Communion/Eucharist",
        "denomination": "Methodist",
        "summary": "Real spiritual presence: Christ is spiritually but not physically present in the elements. The Lord's Supper is a means of grace.",
        "scripture_references": "1 Corinthians 10:16, 1 Corinthians 11:23-26"
    },
    {
        "topic": "Communion/Eucharist",
        "denomination": "Presbyterian",
        "summary": "Spiritual presence: Christ is spiritually present to the faith of believers. The Lord's Supper is a sign and seal of the covenant.",
        "scripture_references": "1 Corinthians 10:16, 1 Corinthians 11:23-26"
    },
    {
        "topic": "Communion/Eucharist",
        "denomination": "Anglican/Episcopal",
        "summary": "Views range from spiritual presence to consubstantiation, but generally affirms Christ's real presence in some form.",
        "scripture_references": "John 6:35-58, 1 Corinthians 11:23-26"
    },
    {
        "topic": "Communion/Eucharist",
        "denomination": "Pentecostal",
        "summary": "Typically a memorial view: the bread and wine are symbols commemorating Christ's death and proclaiming his return.",
        "scripture_references": "1 Corinthians 11:24-26, Luke 22:19"
    }
]

# Create a default admin user
default_user = {
    "username": "admin",
    "email": "admin@example.com",
    "password": "password123",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin"
}

def seed_database():
    """Seed the database with initial data"""
    with app.app_context():
        # Check if data already exists
        if Denomination.query.count() > 0:
            print("Data already exists in the database. Skipping seed.")
            return
        
        # Create denominations
        denom_objects = {}
        for denom_data in denominations:
            denom = Denomination(
                name=denom_data["name"],
                description=denom_data["description"]
            )
            db.session.add(denom)
            denom_objects[denom_data["name"]] = denom
        
        # Need to commit denominations first to get valid IDs
        db.session.commit()
        
        # Create beliefs
        for belief_data in beliefs:
            denom = denom_objects[belief_data["denomination"]]
            belief = Belief(
                topic=belief_data["topic"],
                summary=belief_data["summary"],
                scripture_references=belief_data["scripture_references"],
                denomination_id=denom.id
            )
            db.session.add(belief)
        
        # Create default admin user if no users exist
        if User.query.count() == 0:
            user = User(
                username=default_user["username"],
                email=default_user["email"],
                first_name=default_user["first_name"],
                last_name=default_user["last_name"],
                role=default_user["role"]
            )
            user.password_hash = generate_password_hash(default_user["password"])
            db.session.add(user)
        
        # Commit all changes
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()