[out:json][timeout:30];
area["name:en"="Kowloon City District"]->.outer;
(
  nwr["amenity"~"cafe"](area.outer);
);
out geom;
