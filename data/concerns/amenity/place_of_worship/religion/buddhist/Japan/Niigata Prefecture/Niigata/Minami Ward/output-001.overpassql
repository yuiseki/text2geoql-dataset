[out:json][timeout:30];
area["name:en"="Niigata Prefecture"]->.outer;
area["name:en"="Minami Ward"]->.inner;
(
  nwr["amenity"="place_of_worship"]["religion"="buddhist"](area.inner)(area.outer);
);
out geom;
