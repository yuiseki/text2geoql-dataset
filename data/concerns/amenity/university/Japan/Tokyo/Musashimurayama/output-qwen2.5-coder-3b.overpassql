[out:json][timeout:30];
area["name:en"="Musashimurayama"]->.outer;
(
  nwr["amenity"="university"](area.outer);
);
out geom;
