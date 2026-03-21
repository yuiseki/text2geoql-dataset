[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
(
  nwr["amenity"~"social_facility"](area.outer);
);
out geom;
