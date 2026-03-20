[out:json][timeout:30];
area["name:en"="Kowloon City District"]->.outer;
(
  nwr["amenity"~"bar"](area.outer);
);
out geom;
