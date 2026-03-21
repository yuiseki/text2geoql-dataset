[out:json][timeout:30];
area["name:en"="Kowloon City District"]->.outer;
(
  nwr["amenity"~"restaurant"]["cuisine"~"korean"](area.outer);
);
out geom;
