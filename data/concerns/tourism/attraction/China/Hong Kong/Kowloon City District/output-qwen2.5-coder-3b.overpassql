[out:json][timeout:30];
area["name:en"="Kowloon City District"][boundary=administrative]->.outer;
(
  nwr["tourism"="attraction"](area.outer);
);
out geom;
