[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Dobong-gu"]->.inner;
(
  nwr["amenity"="community_centre"](area.inner)(area.outer);
);
out geom;
