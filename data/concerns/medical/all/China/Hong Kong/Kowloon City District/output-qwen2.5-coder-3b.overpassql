[out:json][timeout:30];
area["name:en"="Kowloon City District"]->.outer;
(
  nwr["amenity"~"hospital|clinic"](area.outer);
);
out geom;
