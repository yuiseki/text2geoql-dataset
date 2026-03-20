[out:json][timeout:30];
area["name:en"="Totsuka Ward"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
