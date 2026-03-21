[out:json][timeout:30];
area["name:en"="Central and Western District"]->.outer;
(
  nwr["amenity"~"dentist"](area.outer);
);
out geom;
