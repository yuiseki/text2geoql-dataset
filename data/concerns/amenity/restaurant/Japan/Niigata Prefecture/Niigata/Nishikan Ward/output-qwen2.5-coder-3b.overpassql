[out:json][timeout:30];
area["name:en"="Niigata"]->.outer;
(
  nwr["amenity"~"restaurant"](area.outer);
);
out geom;
