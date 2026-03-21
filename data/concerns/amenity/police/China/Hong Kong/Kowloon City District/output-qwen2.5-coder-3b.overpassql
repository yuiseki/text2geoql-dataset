[out:json][timeout:30];
area["name:en"="Kowloon City District"]->.outer;
(
  nwr["amenity"~"police"](area.outer);
);
out geom;
