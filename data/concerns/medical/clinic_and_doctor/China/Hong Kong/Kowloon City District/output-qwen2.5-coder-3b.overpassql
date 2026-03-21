[out:json][timeout:30];
area["name:en"="Kowloon City District"]->.outer;
(
  nwr["amenity"~"clinic|doctor"](area.outer);
);
out geom;
