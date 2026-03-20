[out:json][timeout:30];
area["name:en"="Osaka"]->.outer;
area["name:en"="Higashisumiyoshi Ward"]->.inner;
(
  nwr["amenity"="restaurant"]["cuisine"="ramen"](area.inner)(area.outer);
);
out geom;
