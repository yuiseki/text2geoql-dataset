[out:json][timeout:30];
area["name:en"="Saitama"]->.outer;
area["name:en"="Midori Ward"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="sushi"](area.inner)(area.outer);
);
out geom;
