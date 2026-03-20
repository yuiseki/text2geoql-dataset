[out:json][timeout:30];
area["name:en"="Chofu"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
