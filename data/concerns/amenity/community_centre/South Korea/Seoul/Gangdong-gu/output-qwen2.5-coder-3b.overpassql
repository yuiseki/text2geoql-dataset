[out:json][timeout:30];
area["name:en"="Seoul"]->.outer;
area["name:en"="Gangdong-gu"]->.inner;
(
  nwr["amenity"="community_centre"](area.inner)(area.outer);
);
out geom;
