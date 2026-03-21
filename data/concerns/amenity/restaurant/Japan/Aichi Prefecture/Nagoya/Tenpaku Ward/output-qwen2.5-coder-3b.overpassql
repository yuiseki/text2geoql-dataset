[out:json][timeout:30];
area["name:en"="Tenpaku Ward"]->.outer;
(
  nwr["amenity"~"restaurant"](area.outer);
);
out geom;
