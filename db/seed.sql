TRUNCATE users restart identity cascade;
TRUNCATE lists restart identity cascade;
TRUNCATE movies restart identity cascade;

INSERT INTO users(username,email,fname,lname,password) VALUES
('daveb','dave@ga.com','Dave','Buckley','$2b$12$GWwOl7kc3eAQW6gBa39LNOw11uIPm.4a2ex3BLTJ0ysu41aBZDYs6'),
('Chrispy','chris@ga.com','Chris','Smith','$2b$12$2u/y2NryA.QnbjOeJuA7b.yk8kSkHvdgv3FBPfhE9n7gTp/14rn.O');