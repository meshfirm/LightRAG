from __future__ import annotations
from typing import Any

GRAPH_FIELD_SEP = "<SEP>"

PROMPTS: dict[str, Any] = {}

PROMPTS["DEFAULT_LANGUAGE"] = "English"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["organisation", "team", "team member", "customer", "product", "feature", "insight", "decision", "document", "event", "metric", "timeline" ] # original setup: ["organization", "person", "geo", "event", "category"]

PROMPTS["entity_extraction"] = """---Goal---
Given a text document that is potentially relevant to this activity and a list of entity types, identify all entities of those types from the text and all relationships among the identified entities.
Use {language} as output language.

---Entity Type Descriptions---
Here are descriptions of each entity type to help with accurate identification:

- organisation: A company, corporation, business entity, or larger organizational unit. Examples: Microsoft, Tesla, Government Agency.
- team: A group of individuals working together on specific objectives within an organization. Examples: Design Team, Marketing Team, Development Team.
- team member: An individual person who belongs to a team, with specific roles and responsibilities. Examples: Product Manager, Developer, Designer.
- customer: An individual or organization that purchases or uses products/services. Examples: Enterprise Client, Consumer User.
- product: A tangible or digital offering created to meet user needs. Examples: Mobile App, Cloud Service, Hardware Device.
- feature: A distinct capability or component of a product. Examples: User Authentication, Export Functionality, Dashboard.
- insight: A meaningful understanding gained from data, feedback, or observation. Examples: User Pain Point, Market Trend, Usage Pattern.
- decision: A choice or determination made in the product development process. Examples: Feature Prioritization, Design Direction, Go-to-Market Strategy.
- document: A written or digital record containing information. Examples: Requirements Specification, Design Brief, Meeting Notes.
- event: A significant occurrence or milestone. Examples: Product Launch, Review Meeting, User Testing Session.
- metric: A quantifiable measure used to track performance. Examples: User Engagement, Revenue Growth, Development Velocity.
- timeline: A scheduled sequence of tasks, milestones, or deliverables. Examples: Roadmap, Release Schedule, Sprint Plan.

---Steps---
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, use same language as input text. If English, capitalized the name.
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in {language} as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

5. When finished, output {completion_delimiter}

######################
---Examples---
######################
{examples}

#############################
---Real Data---
######################
Entity_types: [{entity_types}]
Text:
{input_text}
######################
Output:"""

PROMPTS["entity_extraction_examples"] = [
    """Example 1:

Entity_types: [organisation, team, team member, customer, product, feature, insight, decision, document, event, metric, timeline]
Text:
```
The Product Development Team at TechNova Inc. held their weekly sprint review yesterday, where Sarah Chen, the lead product manager, presented findings from recent user testing sessions. Enterprise customer Acme Financial had reported difficulties with the dashboard export functionality in the company's flagship analytics platform, DataInsight Pro.

"The CSV export feature is causing 30-second delays when users try to download large datasets," Sarah explained, sharing her screen with detailed error logs. "Our customer satisfaction score for this feature has dropped from 8.2 to 6.5 in the last quarter."

The Engineering Team, represented by Dev Lead Alex Rodriguez, acknowledged the issue and proposed a solution involving database query optimization. After some discussion, the team decided to prioritize this fix for the next sprint cycle, aiming to reduce export times by at least 70%.

This decision was documented in the Sprint Planning Document, which outlines all development priorities for the upcoming two-week sprint. The Product Roadmap was also updated to reflect this change, with the improved export functionality scheduled for release in the v3.2 update next month.

The Marketing Team will measure the success of this initiative using the System Performance Index and Customer Satisfaction scores after the next release.
```

Output:
("entity"{tuple_delimiter}"TechNova Inc."{tuple_delimiter}"organisation"{tuple_delimiter}"TechNova Inc. is a technology company that develops and maintains DataInsight Pro, an analytics platform with dashboard functionality."){record_delimiter}
("entity"{tuple_delimiter}"Product Development Team"{tuple_delimiter}"team"{tuple_delimiter}"The Product Development Team at TechNova Inc. that conducts weekly sprint reviews and makes decisions about product features and priorities."){record_delimiter}
("entity"{tuple_delimiter}"Sarah Chen"{tuple_delimiter}"team member"{tuple_delimiter}"The lead product manager at TechNova Inc. who presented user testing findings and reported on customer satisfaction metrics."){record_delimiter}
("entity"{tuple_delimiter}"Alex Rodriguez"{tuple_delimiter}"team member"{tuple_delimiter}"The Dev Lead representing the Engineering Team who acknowledged export functionality issues and proposed a database query optimization solution."){record_delimiter}
("entity"{tuple_delimiter}"Acme Financial"{tuple_delimiter}"customer"{tuple_delimiter}"An enterprise customer of TechNova Inc. that reported difficulties with the dashboard export functionality in DataInsight Pro."){record_delimiter}
("entity"{tuple_delimiter}"DataInsight Pro"{tuple_delimiter}"product"{tuple_delimiter}"TechNova Inc.'s flagship analytics platform that includes dashboard export functionality among other features."){record_delimiter}
("entity"{tuple_delimiter}"CSV Export Feature"{tuple_delimiter}"feature"{tuple_delimiter}"A functionality in DataInsight Pro that allows users to download data in CSV format, currently experiencing 30-second delays with large datasets."){record_delimiter}
("entity"{tuple_delimiter}"Dashboard Export Issue"{tuple_delimiter}"insight"{tuple_delimiter}"The finding that the CSV export feature causes 30-second delays when users try to download large datasets, impacting customer satisfaction."){record_delimiter}
("entity"{tuple_delimiter}"Query Optimization Decision"{tuple_delimiter}"decision"{tuple_delimiter}"The decision to prioritize fixing the export functionality issue in the next sprint cycle through database query optimization, aiming to reduce export times by at least 70%."){record_delimiter}
("entity"{tuple_delimiter}"Sprint Planning Document"{tuple_delimiter}"document"{tuple_delimiter}"A document outlining all development priorities for the upcoming two-week sprint, including the CSV export functionality fix."){record_delimiter}
("entity"{tuple_delimiter}"Product Roadmap"{tuple_delimiter}"document"{tuple_delimiter}"A document that outlines planned product updates and features, which was updated to include the improved export functionality in v3.2."){record_delimiter}
("entity"{tuple_delimiter}"Weekly Sprint Review"{tuple_delimiter}"event"{tuple_delimiter}"A regular meeting where the Product Development Team discusses progress, issues, and plans, held yesterday when the export functionality issue was addressed."){record_delimiter}
("entity"{tuple_delimiter}"Customer Satisfaction Score"{tuple_delimiter}"metric"{tuple_delimiter}"A numerical measure of customer satisfaction with specific features, which dropped from 8.2 to 6.5 for the CSV export feature in the last quarter."){record_delimiter}
("entity"{tuple_delimiter}"System Performance Index"{tuple_delimiter}"metric"{tuple_delimiter}"A metric that will be used alongside Customer Satisfaction scores to measure the success of the export functionality improvement."){record_delimiter}
("entity"{tuple_delimiter}"Engineering Team"{tuple_delimiter}"team"{tuple_delimiter}"The technical team at TechNova Inc. responsible for implementing fixes and improvements to the product, represented by Dev Lead Alex Rodriguez."){record_delimiter}
("entity"{tuple_delimiter}"Marketing Team"{tuple_delimiter}"team"{tuple_delimiter}"The team responsible for measuring success metrics after product releases."){record_delimiter}
("entity"{tuple_delimiter}"v3.2 Release Timeline"{tuple_delimiter}"timeline"{tuple_delimiter}"The schedule for releasing the improved export functionality in the v3.2 update next month."){record_delimiter}
("entity"{tuple_delimiter}"Two-Week Sprint Cycle"{tuple_delimiter}"timeline"{tuple_delimiter}"The upcoming development period during which the export functionality fix will be implemented."){record_delimiter}
("relationship"{tuple_delimiter}"TechNova Inc."{tuple_delimiter}"DataInsight Pro"{tuple_delimiter}"TechNova Inc. develops and maintains DataInsight Pro as its flagship analytics platform."{tuple_delimiter}"product ownership, development"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"TechNova Inc."{tuple_delimiter}"Product Development Team"{tuple_delimiter}"The Product Development Team is part of TechNova Inc. and responsible for the company's products."{tuple_delimiter}"organizational structure, responsibility"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Sarah Chen"{tuple_delimiter}"Product Development Team"{tuple_delimiter}"Sarah Chen is the lead product manager of the Product Development Team."{tuple_delimiter}"team membership, leadership"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Alex Rodriguez"{tuple_delimiter}"Engineering Team"{tuple_delimiter}"Alex Rodriguez is the Dev Lead of the Engineering Team."{tuple_delimiter}"team membership, leadership"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Acme Financial"{tuple_delimiter}"Dashboard Export Issue"{tuple_delimiter}"Acme Financial reported the difficulties with the dashboard export functionality that led to the identified issue."{tuple_delimiter}"problem reporting, user feedback"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"DataInsight Pro"{tuple_delimiter}"CSV Export Feature"{tuple_delimiter}"The CSV Export Feature is a component of the DataInsight Pro product."{tuple_delimiter}"product feature, functionality"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Dashboard Export Issue"{tuple_delimiter}"Query Optimization Decision"{tuple_delimiter}"The Dashboard Export Issue directly led to the decision to implement query optimization in the next sprint."{tuple_delimiter}"problem solution, prioritization"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Query Optimization Decision"{tuple_delimiter}"Sprint Planning Document"{tuple_delimiter}"The Query Optimization Decision was documented in the Sprint Planning Document."{tuple_delimiter}"decision documentation, planning"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Query Optimization Decision"{tuple_delimiter}"Product Roadmap"{tuple_delimiter}"The Query Optimization Decision resulted in an update to the Product Roadmap to include the improved functionality in v3.2."{tuple_delimiter}"roadmap planning, feature scheduling"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"CSV Export Feature"{tuple_delimiter}"Customer Satisfaction Score"{tuple_delimiter}"Issues with the CSV Export Feature caused the Customer Satisfaction Score to drop from 8.2 to 6.5."{tuple_delimiter}"performance impact, user satisfaction"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Weekly Sprint Review"{tuple_delimiter}"Dashboard Export Issue"{tuple_delimiter}"The Dashboard Export Issue was presented and discussed during the Weekly Sprint Review."{tuple_delimiter}"issue identification, meeting topic"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Query Optimization Decision"{tuple_delimiter}"v3.2 Release Timeline"{tuple_delimiter}"The Query Optimization Decision is scheduled to be implemented according to the v3.2 Release Timeline."{tuple_delimiter}"implementation planning, release scheduling"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Marketing Team"{tuple_delimiter}"System Performance Index"{tuple_delimiter}"The Marketing Team will use the System Performance Index to measure the success of the export functionality improvement."{tuple_delimiter}"performance measurement, success tracking"{tuple_delimiter}8){record_delimiter}
("content_keywords"{tuple_delimiter}"product development, performance issues, customer satisfaction, sprint planning, feature optimization, export functionality, data analytics, team collaboration"){completion_delimiter}
#############################""",
    """Example 2:

Entity_types: [organisation, team, team member, customer, product, feature, insight, decision, document, event, metric, timeline]
Text:
```
GlobalSoft Solutions' Executive Team convened for the Q3 Strategic Planning Meeting last Tuesday. CEO Jennifer Park opened by highlighting a concerning trend from the latest Market Penetration Report: their enterprise collaboration tool, WorkStream, was losing market share to competitors offering better mobile experiences.

The Customer Research Team, led by Marcus Washington, presented insights from recent interviews with key clients like Meridian Healthcare and BlueSky Retail. "82% of enterprise users now consider mobile access critical, compared to just 47% last year," Marcus explained. "Our app's user engagement score is 3.6/10, well below industry average of 7.2."

CTO Raj Patel and his Mobile Development Team proposed an aggressive redesign of the WorkStream mobile app, focusing on offline functionality and push notifications—two features frequently requested in customer feedback.

After thorough discussion, the leadership team decided to allocate additional resources to mobile development, targeting a complete app redesign for Q1 next year. This decision was documented in the updated Product Strategy Document and Annual Investment Plan.

The project will follow an accelerated timeline, with design completion by November 15th, development by February 1st, and public release by March 20th. Success will be measured primarily through the Mobile User Satisfaction Index and app engagement metrics, with a target of 40% improvement in both areas within two months of release.
```

Output:
("entity"{tuple_delimiter}"GlobalSoft Solutions"{tuple_delimiter}"organisation"{tuple_delimiter}"A company that develops enterprise collaboration tools, including WorkStream, and is facing challenges with mobile market share."){record_delimiter}
("entity"{tuple_delimiter}"Executive Team"{tuple_delimiter}"team"{tuple_delimiter}"The senior leadership group at GlobalSoft Solutions that makes strategic decisions about product direction and resource allocation."){record_delimiter}
("entity"{tuple_delimiter}"Customer Research Team"{tuple_delimiter}"team"{tuple_delimiter}"The team responsible for gathering and analyzing customer feedback and market insights, led by Marcus Washington."){record_delimiter}
("entity"{tuple_delimiter}"Mobile Development Team"{tuple_delimiter}"team"{tuple_delimiter}"The technical team at GlobalSoft Solutions responsible for developing mobile applications, working under CTO Raj Patel."){record_delimiter}
("entity"{tuple_delimiter}"Jennifer Park"{tuple_delimiter}"team member"{tuple_delimiter}"The CEO of GlobalSoft Solutions who highlighted market share concerns during the strategic planning meeting."){record_delimiter}
("entity"{tuple_delimiter}"Marcus Washington"{tuple_delimiter}"team member"{tuple_delimiter}"The leader of the Customer Research Team who presented insights from customer interviews and engagement metrics."){record_delimiter}
("entity"{tuple_delimiter}"Raj Patel"{tuple_delimiter}"team member"{tuple_delimiter}"The CTO of GlobalSoft Solutions who proposed the mobile app redesign with his team."){record_delimiter}
("entity"{tuple_delimiter}"Meridian Healthcare"{tuple_delimiter}"customer"{tuple_delimiter}"A key client of GlobalSoft Solutions that participated in recent interviews conducted by the Customer Research Team."){record_delimiter}
("entity"{tuple_delimiter}"BlueSky Retail"{tuple_delimiter}"customer"{tuple_delimiter}"A key client of GlobalSoft Solutions that participated in recent interviews conducted by the Customer Research Team."){record_delimiter}
("entity"{tuple_delimiter}"WorkStream"{tuple_delimiter}"product"{tuple_delimiter}"An enterprise collaboration tool developed by GlobalSoft Solutions that is losing market share due to inadequate mobile experience."){record_delimiter}
("entity"{tuple_delimiter}"WorkStream Mobile App"{tuple_delimiter}"product"{tuple_delimiter}"The mobile version of WorkStream that has low user engagement scores and requires redesign."){record_delimiter}
("entity"{tuple_delimiter}"Offline Functionality"{tuple_delimiter}"feature"{tuple_delimiter}"A capability frequently requested by customers that allows the mobile app to work without internet connection."){record_delimiter}
("entity"{tuple_delimiter}"Push Notifications"{tuple_delimiter}"feature"{tuple_delimiter}"A mobile app feature frequently requested by customers that alerts users of important updates or actions."){record_delimiter}
("entity"{tuple_delimiter}"Mobile Importance Trend"{tuple_delimiter}"insight"{tuple_delimiter}"The insight that 82% of enterprise users now consider mobile access critical, up from 47% last year."){record_delimiter}
("entity"{tuple_delimiter}"Low Mobile Engagement"{tuple_delimiter}"insight"{tuple_delimiter}"The finding that the WorkStream mobile app's user engagement score is 3.6/10, well below the industry average of 7.2."){record_delimiter}
("entity"{tuple_delimiter}"Mobile Redesign Decision"{tuple_delimiter}"decision"{tuple_delimiter}"The decision to allocate additional resources to mobile development for a complete app redesign targeted for Q1 next year."){record_delimiter}
("entity"{tuple_delimiter}"Product Strategy Document"{tuple_delimiter}"document"{tuple_delimiter}"A document that was updated to reflect the decision to prioritize the mobile app redesign."){record_delimiter}
("entity"{tuple_delimiter}"Annual Investment Plan"{tuple_delimiter}"document"{tuple_delimiter}"A document outlining resource allocation that was updated to include additional funding for mobile development."){record_delimiter}
("entity"{tuple_delimiter}"Market Penetration Report"{tuple_delimiter}"document"{tuple_delimiter}"A report highlighting market trends, including WorkStream's loss of market share to competitors with better mobile experiences."){record_delimiter}
("entity"{tuple_delimiter}"Q3 Strategic Planning Meeting"{tuple_delimiter}"event"{tuple_delimiter}"A meeting where GlobalSoft's Executive Team discussed strategic priorities, including the mobile app redesign."){record_delimiter}
("entity"{tuple_delimiter}"Mobile User Satisfaction Index"{tuple_delimiter}"metric"{tuple_delimiter}"A key performance indicator that will be used to measure the success of the mobile app redesign, targeting a 40% improvement."){record_delimiter}
("entity"{tuple_delimiter}"App Engagement Metrics"{tuple_delimiter}"metric"{tuple_delimiter}"Measurements of how users interact with the mobile app, currently at 3.6/10, with a target of 40% improvement after redesign."){record_delimiter}
("entity"{tuple_delimiter}"Mobile Redesign Timeline"{tuple_delimiter}"timeline"{tuple_delimiter}"The schedule for completing the mobile app redesign, including design completion by November 15th, development by February 1st, and release by March 20th."){record_delimiter}
("relationship"{tuple_delimiter}"GlobalSoft Solutions"{tuple_delimiter}"WorkStream"{tuple_delimiter}"GlobalSoft Solutions develops and owns WorkStream as their enterprise collaboration tool."{tuple_delimiter}"product ownership, development"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"GlobalSoft Solutions"{tuple_delimiter}"Executive Team"{tuple_delimiter}"The Executive Team leads GlobalSoft Solutions and makes strategic decisions for the company."{tuple_delimiter}"organizational leadership, governance"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Jennifer Park"{tuple_delimiter}"Executive Team"{tuple_delimiter}"Jennifer Park is the CEO and a key member of the Executive Team at GlobalSoft Solutions."{tuple_delimiter}"team membership, leadership"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Marcus Washington"{tuple_delimiter}"Customer Research Team"{tuple_delimiter}"Marcus Washington leads the Customer Research Team at GlobalSoft Solutions."{tuple_delimiter}"team leadership, management"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Raj Patel"{tuple_delimiter}"Mobile Development Team"{tuple_delimiter}"Raj Patel is the CTO who oversees the Mobile Development Team at GlobalSoft Solutions."{tuple_delimiter}"team oversight, technical leadership"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Meridian Healthcare"{tuple_delimiter}"Mobile Importance Trend"{tuple_delimiter}"Meridian Healthcare, as a key client, contributed to the insight about increasing importance of mobile access."{tuple_delimiter}"customer input, market trend"{tuple_delimiter}7){record_delimiter}
("relationship"{tuple_delimiter}"WorkStream"{tuple_delimiter}"WorkStream Mobile App"{tuple_delimiter}"The WorkStream Mobile App is the mobile version of the WorkStream collaboration tool."{tuple_delimiter}"product component, mobile extension"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"WorkStream Mobile App"{tuple_delimiter}"Low Mobile Engagement"{tuple_delimiter}"The WorkStream Mobile App has a low user engagement score of 3.6/10, well below industry average."{tuple_delimiter}"performance issue, user dissatisfaction"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Low Mobile Engagement"{tuple_delimiter}"Mobile Redesign Decision"{tuple_delimiter}"The Low Mobile Engagement insight directly contributed to the Mobile Redesign Decision."{tuple_delimiter}"problem identification, solution planning"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Mobile Redesign Decision"{tuple_delimiter}"Product Strategy Document"{tuple_delimiter}"The Mobile Redesign Decision was documented in the updated Product Strategy Document."{tuple_delimiter}"decision documentation, strategic planning"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Mobile Redesign Decision"{tuple_delimiter}"Annual Investment Plan"{tuple_delimiter}"The Mobile Redesign Decision resulted in updates to the Annual Investment Plan to allocate additional resources."{tuple_delimiter}"resource allocation, financial planning"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Mobile Development Team"{tuple_delimiter}"Offline Functionality"{tuple_delimiter}"The Mobile Development Team will implement the Offline Functionality as part of the app redesign."{tuple_delimiter}"feature development, technical implementation"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Mobile Development Team"{tuple_delimiter}"Push Notifications"{tuple_delimiter}"The Mobile Development Team will implement Push Notifications as part of the app redesign."{tuple_delimiter}"feature development, technical implementation"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Q3 Strategic Planning Meeting"{tuple_delimiter}"Mobile Redesign Decision"{tuple_delimiter}"The Mobile Redesign Decision was made during the Q3 Strategic Planning Meeting."{tuple_delimiter}"decision making, strategic discussion"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Mobile Redesign Decision"{tuple_delimiter}"Mobile Redesign Timeline"{tuple_delimiter}"The Mobile Redesign Decision will be implemented according to the Mobile Redesign Timeline."{tuple_delimiter}"project planning, implementation schedule"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Mobile User Satisfaction Index"{tuple_delimiter}"Mobile Redesign Decision"{tuple_delimiter}"The Mobile User Satisfaction Index will be used to measure the success of the Mobile Redesign Decision, with a target of 40% improvement."{tuple_delimiter}"performance measurement, success criteria"{tuple_delimiter}8){record_delimiter}
("content_keywords"{tuple_delimiter}"mobile development, strategic planning, customer research, market trends, app redesign, enterprise collaboration, user engagement, product strategy"){completion_delimiter}
#############################""",
    """Example 3:

Entity_types: [organisation, team, team member, customer, product, feature, insight, decision, document, event, metric, timeline]
Text:
```
During yesterday's User Feedback Session, NovaTech's Product Team gathered input from beta users of their SmartTask project management application. Lead Designer Emma Rodriguez demonstrated the new Task Dependencies Feature, which allows users to create visual workflows between related tasks.

FutureWorks Inc., a midsize marketing agency and pilot customer, provided valuable feedback through their Project Director, David Chen. "The dependency visualization is powerful, but we need the ability to set conditional dependencies based on task status," Chen explained.

This insight resonated with findings from the recent Customer Needs Assessment, which identified advanced dependency management as a top request among enterprise users. After the session, Product Owner Jason Kim and the Development Team conducted a quick analysis and determined that implementing conditional dependencies would require approximately three weeks of development time.

In the Post-Session Debrief, the team decided to add this enhancement to the Q2 Development Roadmap, targeting inclusion in the 3.5 release. This decision was recorded in the Product Requirements Document, along with specific user stories and acceptance criteria.

Success will be measured using the Feature Adoption Rate and the Task Management Efficiency Score, with a baseline to be established immediately after release.
```

Output:
("entity"{tuple_delimiter}"NovaTech"{tuple_delimiter}"organisation"{tuple_delimiter}"The company that develops the SmartTask project management application and conducted the User Feedback Session."){record_delimiter}
("entity"{tuple_delimiter}"Product Team"{tuple_delimiter}"team"{tuple_delimiter}"NovaTech's team responsible for gathering user feedback and making product decisions for SmartTask."){record_delimiter}
("entity"{tuple_delimiter}"Development Team"{tuple_delimiter}"team"{tuple_delimiter}"NovaTech's team responsible for implementing features and enhancements to SmartTask."){record_delimiter}
("entity"{tuple_delimiter}"Emma Rodriguez"{tuple_delimiter}"team member"{tuple_delimiter}"The Lead Designer at NovaTech who demonstrated the new Task Dependencies Feature during the User Feedback Session."){record_delimiter}
("entity"{tuple_delimiter}"Jason Kim"{tuple_delimiter}"team member"{tuple_delimiter}"The Product Owner at NovaTech who, along with the Development Team, analyzed the feasibility of implementing conditional dependencies."){record_delimiter}
("entity"{tuple_delimiter}"David Chen"{tuple_delimiter}"team member"{tuple_delimiter}"The Project Director at FutureWorks Inc. who provided feedback about needing conditional dependencies based on task status."){record_delimiter}
("entity"{tuple_delimiter}"FutureWorks Inc."{tuple_delimiter}"customer"{tuple_delimiter}"A midsize marketing agency and pilot customer of NovaTech's SmartTask application."){record_delimiter}
("entity"{tuple_delimiter}"SmartTask"{tuple_delimiter}"product"{tuple_delimiter}"A project management application developed by NovaTech that includes features like task dependencies."){record_delimiter}
("entity"{tuple_delimiter}"Task Dependencies Feature"{tuple_delimiter}"feature"{tuple_delimiter}"A feature in SmartTask that allows users to create visual workflows between related tasks."){record_delimiter}
("entity"{tuple_delimiter}"Conditional Dependencies"{tuple_delimiter}"feature"{tuple_delimiter}"A requested enhancement to the Task Dependencies Feature that would allow dependencies based on task status."){record_delimiter}
("entity"{tuple_delimiter}"Dependency Enhancement Need"{tuple_delimiter}"insight"{tuple_delimiter}"The insight that users need the ability to set conditional dependencies based on task status, which aligns with findings from the Customer Needs Assessment."){record_delimiter}
("entity"{tuple_delimiter}"Enterprise User Preference"{tuple_delimiter}"insight"{tuple_delimiter}"The finding from the Customer Needs Assessment that advanced dependency management is a top request among enterprise users."){record_delimiter}
("entity"{tuple_delimiter}"Feature Implementation Decision"{tuple_delimiter}"decision"{tuple_delimiter}"The decision to add conditional dependencies enhancement to the Q2 Development Roadmap, targeting inclusion in the 3.5 release."){record_delimiter}
("entity"{tuple_delimiter}"Product Requirements Document"{tuple_delimiter}"document"{tuple_delimiter}"A document where the decision to implement conditional dependencies was recorded, along with user stories and acceptance criteria."){record_delimiter}
("entity"{tuple_delimiter}"Customer Needs Assessment"{tuple_delimiter}"document"{tuple_delimiter}"A research document that identified advanced dependency management as a top request among enterprise users."){record_delimiter}
("entity"{tuple_delimiter}"User Feedback Session"{tuple_delimiter}"event"{tuple_delimiter}"An event where NovaTech's Product Team gathered input from beta users of SmartTask, including demonstration of the Task Dependencies Feature."){record_delimiter}
("entity"{tuple_delimiter}"Post-Session Debrief"{tuple_delimiter}"event"{tuple_delimiter}"A meeting after the User Feedback Session where the team decided to add conditional dependencies to the roadmap."){record_delimiter}
("entity"{tuple_delimiter}"Feature Adoption Rate"{tuple_delimiter}"metric"{tuple_delimiter}"A metric that will be used to measure the success of the conditional dependencies feature after release."){record_delimiter}
("entity"{tuple_delimiter}"Task Management Efficiency Score"{tuple_delimiter}"metric"{tuple_delimiter}"A metric that will be used to measure the success of the conditional dependencies feature after release."){record_delimiter}
("entity"{tuple_delimiter}"Q2 Development Roadmap"{tuple_delimiter}"timeline"{tuple_delimiter}"The schedule for upcoming development work, which now includes the conditional dependencies enhancement."){record_delimiter}
("entity"{tuple_delimiter}"Three-Week Development Estimate"{tuple_delimiter}"timeline"{tuple_delimiter}"The estimated time required to implement the conditional dependencies feature."){record_delimiter}
("relationship"{tuple_delimiter}"NovaTech"{tuple_delimiter}"SmartTask"{tuple_delimiter}"NovaTech develops the SmartTask project management application."{tuple_delimiter}"product development, ownership"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"NovaTech"{tuple_delimiter}"Product Team"{tuple_delimiter}"The Product Team is part of NovaTech and responsible for the SmartTask product."{tuple_delimiter}"organizational structure, team responsibility"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Emma Rodriguez"{tuple_delimiter}"Product Team"{tuple_delimiter}"Emma Rodriguez is the Lead Designer in NovaTech's Product Team."{tuple_delimiter}"team membership, design leadership"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Jason Kim"{tuple_delimiter}"Product Team"{tuple_delimiter}"Jason Kim is the Product Owner in NovaTech's Product Team."{tuple_delimiter}"team membership, product ownership"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"FutureWorks Inc."{tuple_delimiter}"SmartTask"{tuple_delimiter}"FutureWorks Inc. is a pilot customer using NovaTech's SmartTask application."{tuple_delimiter}"customer relationship, product usage"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"David Chen"{tuple_delimiter}"FutureWorks Inc."{tuple_delimiter}"David Chen is the Project Director at FutureWorks Inc."{tuple_delimiter}"employment, leadership role"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"SmartTask"{tuple_delimiter}"Task Dependencies Feature"{tuple_delimiter}"The Task Dependencies Feature is a component of the SmartTask application."{tuple_delimiter}"product feature, functionality"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Task Dependencies Feature"{tuple_delimiter}"Conditional Dependencies"{tuple_delimiter}"Conditional Dependencies is a requested enhancement to the existing Task Dependencies Feature."{tuple_delimiter}"feature enhancement, functionality extension"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"FutureWorks Inc."{tuple_delimiter}"Dependency Enhancement Need"{tuple_delimiter}"FutureWorks Inc., through David Chen, expressed the need for conditional dependencies based on task status."{tuple_delimiter}"customer feedback, feature request"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Dependency Enhancement Need"{tuple_delimiter}"Enterprise User Preference"{tuple_delimiter}"The need for conditional dependencies aligns with the finding that advanced dependency management is a top request among enterprise users."{tuple_delimiter}"insight validation, user preference"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Dependency Enhancement Need"{tuple_delimiter}"Feature Implementation Decision"{tuple_delimiter}"The identified need for conditional dependencies led to the decision to implement this enhancement."{tuple_delimiter}"requirement gathering, feature planning"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Feature Implementation Decision"{tuple_delimiter}"Product Requirements Document"{tuple_delimiter}"The decision to implement conditional dependencies was recorded in the Product Requirements Document."{tuple_delimiter}"decision documentation, requirements specification"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Feature Implementation Decision"{tuple_delimiter}"Q2 Development Roadmap"{tuple_delimiter}"The decision to implement conditional dependencies resulted in adding this enhancement to the Q2 Development Roadmap."{tuple_delimiter}"roadmap planning, feature scheduling"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"User Feedback Session"{tuple_delimiter}"Dependency Enhancement Need"{tuple_delimiter}"The Dependency Enhancement Need was identified during the User Feedback Session."{tuple_delimiter}"feedback gathering, need identification"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Post-Session Debrief"{tuple_delimiter}"Feature Implementation Decision"{tuple_delimiter}"The Feature Implementation Decision was made during the Post-Session Debrief."{tuple_delimiter}"decision making, planning"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Development Team"{tuple_delimiter}"Three-Week Development Estimate"{tuple_delimiter}"The Development Team determined that implementing conditional dependencies would require the Three-Week Development Estimate."{tuple_delimiter}"estimation, development planning"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"Feature Adoption Rate"{tuple_delimiter}"Conditional Dependencies"{tuple_delimiter}"The Feature Adoption Rate will be used to measure how widely the Conditional Dependencies feature is used after release."{tuple_delimiter}"success measurement, usage tracking"{tuple_delimiter}7){record_delimiter}
("content_keywords"{tuple_delimiter}"user feedback, project management, feature enhancement, product development, task dependencies, customer needs, roadmap planning, agile development"){completion_delimiter}
#############################"""
]

PROMPTS[
    "summarize_entity_descriptions"
] = """You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we the have full context.
Use {language} as output language.

#######
---Data---
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""

PROMPTS["entity_continue_extraction"] = """
MANY entities and relationships were missed in the last extraction.

---Remember Steps---

1. Identify all entities. For each identified entity, extract the following information:
- entity_name: Name of the entity, use same language as input text. If English, capitalized the name.
- entity_type: One of the following types: [{entity_types}]
- entity_description: Comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>

2. From the entities identified in step 1, identify all pairs of (source_entity, target_entity) that are *clearly related* to each other.
For each pair of related entities, extract the following information:
- source_entity: name of the source entity, as identified in step 1
- target_entity: name of the target entity, as identified in step 1
- relationship_description: explanation as to why you think the source entity and the target entity are related to each other
- relationship_strength: a numeric score indicating strength of the relationship between the source entity and target entity
- relationship_keywords: one or more high-level key words that summarize the overarching nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level key words that summarize the main concepts, themes, or topics of the entire text. These should capture the overarching ideas present in the document.
Format the content-level key words as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in {language} as a single list of all the entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

5. When finished, output {completion_delimiter}

---Output---

Add them below using the same format:\n
""".strip()

PROMPTS["entity_if_loop_extraction"] = """
---Goal---'

It appears some entities may have still been missed.

---Output---

Answer ONLY by `YES` OR `NO` if there are still entities that need to be added.
""".strip()

PROMPTS["fail_response"] = (
    "Sorry, I'm not able to provide an answer to that question.[no-context]"
)

PROMPTS["rag_response"] = """---Role---

You are a helpful assistant responding to user query about Knowledge Base provided below.


---Goal---

Generate a concise response based on Knowledge Base and follow Response Rules, considering both the conversation history and the current query. Summarize all information in the provided Knowledge Base, and incorporating general knowledge relevant to the Knowledge Base. Do not include information not provided by Knowledge Base.

When handling relationships with timestamps:
1. Each relationship has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting relationships, consider both the semantic content and the timestamp
3. Don't automatically prefer the most recently created relationships - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Knowledge Base---
{context_data}

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with appropriate section headings
- Please respond in the same language as the user's question.
- Ensure the response maintains continuity with the conversation history.
- List up to 5 most important reference sources at the end under "References" section. Clearly indicating whether each source is from Knowledge Graph (KG) or Vector Data (DC), and include the file path if available, in the following format: [KG/DC] file_path
- If you don't know the answer, just say so.
- Do not make anything up. Do not include information not provided by the Knowledge Base."""

PROMPTS["keywords_extraction"] = """---Role---

You are a helpful assistant tasked with identifying both high-level and low-level keywords in the user's query and conversation history.

---Goal---

Given the query and conversation history, list both high-level and low-level keywords. High-level keywords focus on overarching concepts or themes, while low-level keywords focus on specific entities, details, or concrete terms.

---Instructions---

- Consider both the current query and relevant conversation history when extracting keywords
- Output the keywords in JSON format, it will be parsed by a JSON parser, do not add any extra content in output
- The JSON should have two keys:
  - "high_level_keywords" for overarching concepts or themes
  - "low_level_keywords" for specific entities or details

######################
---Examples---
######################
{examples}

#############################
---Real Data---
######################
Conversation History:
{history}

Current Query: {query}
######################
The `Output` should be human text, not unicode characters. Keep the same language as `Query`.
Output:

"""

PROMPTS["keywords_extraction_examples"] = [
    """Example 1:

Query: "How does international trade influence global economic stability?"
################
Output:
{
  "high_level_keywords": ["International trade", "Global economic stability", "Economic impact"],
  "low_level_keywords": ["Trade agreements", "Tariffs", "Currency exchange", "Imports", "Exports"]
}
#############################""",
    """Example 2:

Query: "What are the environmental consequences of deforestation on biodiversity?"
################
Output:
{
  "high_level_keywords": ["Environmental consequences", "Deforestation", "Biodiversity loss"],
  "low_level_keywords": ["Species extinction", "Habitat destruction", "Carbon emissions", "Rainforest", "Ecosystem"]
}
#############################""",
    """Example 3:

Query: "What is the role of education in reducing poverty?"
################
Output:
{
  "high_level_keywords": ["Education", "Poverty reduction", "Socioeconomic development"],
  "low_level_keywords": ["School access", "Literacy rates", "Job training", "Income inequality"]
}
#############################""",
]


PROMPTS["naive_rag_response"] = """---Role---

You are a helpful assistant responding to user query about Document Chunks provided below.

---Goal---

Generate a concise response based on Document Chunks and follow Response Rules, considering both the conversation history and the current query. Summarize all information in the provided Document Chunks, and incorporating general knowledge relevant to the Document Chunks. Do not include information not provided by Document Chunks.

When handling content with timestamps:
1. Each piece of content has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting information, consider both the content and the timestamp
3. Don't automatically prefer the most recent content - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Document Chunks---
{content_data}

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with appropriate section headings
- Please respond in the same language as the user's question.
- Ensure the response maintains continuity with the conversation history.
- List up to 5 most important reference sources at the end under "References" section. Clearly indicating whether each source is from Knowledge Graph (KG) or Vector Data (DC), and include the file path if available, in the following format: [KG/DC] file_path
- If you don't know the answer, just say so.
- Do not include information not provided by the Document Chunks."""


PROMPTS[
    "similarity_check"
] = """Please analyze the similarity between these two questions:

Question 1: {original_prompt}
Question 2: {cached_prompt}

Please evaluate whether these two questions are semantically similar, and whether the answer to Question 2 can be used to answer Question 1, provide a similarity score between 0 and 1 directly.

Similarity score criteria:
0: Completely unrelated or answer cannot be reused, including but not limited to:
   - The questions have different topics
   - The locations mentioned in the questions are different
   - The times mentioned in the questions are different
   - The specific individuals mentioned in the questions are different
   - The specific events mentioned in the questions are different
   - The background information in the questions is different
   - The key conditions in the questions are different
1: Identical and answer can be directly reused
0.5: Partially related and answer needs modification to be used
Return only a number between 0-1, without any additional content.
"""

PROMPTS["mix_rag_response"] = """---Role---

You are a helpful assistant responding to user query about Data Sources provided below.


---Goal---

Generate a concise response based on Data Sources and follow Response Rules, considering both the conversation history and the current query. Data sources contain two parts: Knowledge Graph(KG) and Document Chunks(DC). Summarize all information in the provided Data Sources, and incorporating general knowledge relevant to the Data Sources. Do not include information not provided by Data Sources.

When handling information with timestamps:
1. Each piece of information (both relationships and content) has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting information, consider both the content/relationship and the timestamp
3. Don't automatically prefer the most recent information - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Data Sources---

1. From Knowledge Graph(KG):
{kg_context}

2. From Document Chunks(DC):
{vector_context}

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with appropriate section headings
- Please respond in the same language as the user's question.
- Ensure the response maintains continuity with the conversation history.
- Organize answer in sections focusing on one main point or aspect of the answer
- Use clear and descriptive section titles that reflect the content
- List up to 5 most important reference sources at the end under "References" section. Clearly indicating whether each source is from Knowledge Graph (KG) or Vector Data (DC), and include the file path if available, in the following format: [KG/DC] file_path
- If you don't know the answer, just say so. Do not make anything up.
- Do not include information not provided by the Data Sources."""
