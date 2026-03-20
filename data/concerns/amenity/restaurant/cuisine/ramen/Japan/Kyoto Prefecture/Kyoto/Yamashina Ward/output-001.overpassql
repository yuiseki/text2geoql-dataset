[out:json][timeout:30];
area["name:en"="Kyoto"]->.outer;
area["name:en"="Yamashina Ward"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="ramen"](area.inner)(area.outer);
);
out geom;
