[out:json][timeout:30];
area["name:en"="Minami Ward"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
